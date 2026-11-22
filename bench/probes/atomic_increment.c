// Extra, not part of RQ1 or RQ2: a C microbenchmark of the shared atomic histogram with the
// increment sequences that LLVM and V8's two compilers emit, to test whether the instructions of
// one increment explain how the atomic histogram's time differs between environments.
//
// Build: cc -O2 -pthread -masm=intel -o atomic_increment bench/probes/atomic_increment.c
// Run:   on the measured cores, e.g. inside a run scope; prints one CSV row per timed pass.

#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define PIXELS (8192UL * 8192UL)
#define BINS 256
// The bench pads each counter to 128 bytes and indexes the table with the pixel value << 7.
#define STRIDE 128
// The seed and the generator of the study's few-colours input (bench/src/input).
#define SEED 24301ULL
#define ROUNDS 10
#define WARMUP_PASSES 2
#define MAX_THREADS 8
// Thread i runs on CPU 2 * i: the P-cores of the measuring PC are the even CPUs 0 to 14.
#define CPU_STEP 2

static uint8_t table[BINS * STRIDE] __attribute__((aligned(STRIDE)));

// Eight increments per turn, as LLVM unrolls the bench's loop. %0 is the pixel pointer, %1 its
// end, %2 the table, %3 the table's end (for the bounds check of the checked sequences).
#define LOOP(step)                                                                              \
    __asm__ volatile("1:\n" step(0) step(1) step(2) step(3) step(4) step(5) step(6) step(7)     \
                     "add %0, 8\n cmp %0, %1\n jne 1b\n 9:\n"                                   \
                     : "+r"(pixel)                                                              \
                     : "r"(end), "r"(counters), "r"(counters + BINS * STRIDE)                   \
                     : "rax", "rcx", "rdx", "memory", "cc")

#define INDEX(o) "movzx ecx, byte ptr [%0+" #o "]\n shl ecx, 7\n"
// An alignment check and a bounds check before the access, as V8's baseline compiler emits
// them; neither branch is ever taken here.
#define CHECKS "mov eax, ecx\n and eax, 7\n test eax, eax\n jne 9f\n lea rax, [%2+rcx+7]\n cmp rax, %3\n jae 9f\n"

// LLVM, native: one locked increment.
#define S_INC(o) INDEX(o) "lock inc qword ptr [%2+rcx]\n"
// V8's optimizing compiler: load, add, compare-and-swap, again from the load if it failed.
#define S_CAS(o) INDEX(o) "2:\n mov rax, qword ptr [%2+rcx]\n lea rdx, [rax+1]\n lock cmpxchg qword ptr [%2+rcx], rdx\n jne 2b\n"
// V8's baseline compiler: one locked exchange-and-add.
#define S_XADD(o) INDEX(o) "mov edx, 1\n lock xadd qword ptr [%2+rcx], rdx\n"
#define S_INC_CHECKED(o) INDEX(o) CHECKS "lock inc qword ptr [%2+rcx]\n"
#define S_XADD_CHECKED(o) INDEX(o) CHECKS "mov edx, 1\n lock xadd qword ptr [%2+rcx], rdx\n"

#define SEQUENCE(name, step)                                                                    \
    static void name(const uint8_t *pixel, const uint8_t *end, uint8_t *counters) { LOOP(step); }

SEQUENCE(lock_inc, S_INC)
SEQUENCE(compare_and_swap, S_CAS)
SEQUENCE(lock_xadd, S_XADD)
SEQUENCE(lock_inc_checked, S_INC_CHECKED)
SEQUENCE(lock_xadd_checked, S_XADD_CHECKED)

typedef void (*sequence)(const uint8_t *, const uint8_t *, uint8_t *);

struct task {
    sequence run;
    const uint8_t *begin, *end;
    int cpu;
    pthread_barrier_t *start;
};

// https://prng.di.unimi.it/splitmix64.c
static uint64_t split_mix64(uint64_t *state) {
    uint64_t z = (*state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

// k values spread over the 256 counters, drawn as the bench draws them.
static void fill(uint8_t *image, unsigned k) {
    uint64_t state = SEED;
    for (size_t i = 0; i < PIXELS; i++) image[i] = (uint8_t)(split_mix64(&state) % k * (BINS / k));
}

static void *work(void *argument) {
    struct task *task = argument;
    cpu_set_t cpus;
    CPU_ZERO(&cpus);
    CPU_SET(task->cpu, &cpus);
    if (pthread_setaffinity_np(pthread_self(), sizeof cpus, &cpus) != 0) {
        fprintf(stderr, "cannot run on CPU %d\n", task->cpu);
        exit(1);
    }
    pthread_barrier_wait(task->start);
    task->run(task->begin, task->end, table);
    return NULL;
}

static uint64_t now_ns(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ULL + (uint64_t)t.tv_nsec;
}

// One pass over the image with each thread on its own slice and core. The threads are created
// and pinned before the clock starts; the clock stops when the last one has finished.
static uint64_t pass(sequence run, const uint8_t *image, int threads) {
    pthread_t workers[MAX_THREADS];
    struct task tasks[MAX_THREADS];
    pthread_barrier_t start;
    size_t slice = PIXELS / (size_t)threads;
    memset(table, 0, sizeof table);
    pthread_barrier_init(&start, NULL, (unsigned)threads + 1);
    for (int i = 0; i < threads; i++) {
        tasks[i] = (struct task){run, image + (size_t)i * slice, image + (size_t)(i + 1) * slice, i * CPU_STEP, &start};
        pthread_create(&workers[i], NULL, work, &tasks[i]);
    }
    uint64_t begin = now_ns();
    pthread_barrier_wait(&start);
    for (int i = 0; i < threads; i++) pthread_join(workers[i], NULL);
    uint64_t elapsed = now_ns() - begin;
    pthread_barrier_destroy(&start);
    return elapsed;
}

static int counted_every_pixel(void) {
    uint64_t total = 0;
    for (int bin = 0; bin < BINS; bin++) total += *(uint64_t *)(table + bin * STRIDE);
    return total == PIXELS;
}

int main(void) {
    static const struct { const char *name; sequence run; } sequences[] = {
        {"lock-inc", lock_inc},
        {"compare-and-swap", compare_and_swap},
        {"lock-xadd", lock_xadd},
        {"lock-inc-checked", lock_inc_checked},
        {"lock-xadd-checked", lock_xadd_checked},
    };
    static const unsigned ks[] = {1, 16, 256};
    static const int thread_counts[] = {1, MAX_THREADS};
    enum { SEQUENCES = sizeof sequences / sizeof *sequences, KS = sizeof ks / sizeof *ks, COUNTS = sizeof thread_counts / sizeof *thread_counts };
    uint8_t *images[KS];
    for (int k = 0; k < KS; k++) {
        images[k] = aligned_alloc(4096, PIXELS);
        fill(images[k], ks[k]);
    }
    printf("sequence,k,threads,round,ns,counted\n");
    // Every cell once per round, so that a drift of the machine falls on all of them alike.
    for (int round = -WARMUP_PASSES; round < ROUNDS; round++)
        for (int k = 0; k < KS; k++)
            for (int c = 0; c < COUNTS; c++)
                for (int s = 0; s < SEQUENCES; s++) {
                    uint64_t ns = pass(sequences[s].run, images[k], thread_counts[c]);
                    if (round >= 0)
                        printf("%s,%u,%d,%d,%llu,%s\n", sequences[s].name, ks[k], thread_counts[c], round,
                               (unsigned long long)ns, counted_every_pixel() ? "yes" : "NO");
                    fflush(stdout);
                }
    return 0;
}
