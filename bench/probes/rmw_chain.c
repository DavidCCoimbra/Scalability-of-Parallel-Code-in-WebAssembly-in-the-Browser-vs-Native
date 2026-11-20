// Extra, not part of RQ1 or RQ2: a C microbenchmark of the increment sequences the compilers
// emit for the k = 1 local histogram, to explain why one environment's loop is faster.

#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define PIXELS (8192UL * 8192UL)

static uint64_t counts[256 + 2048] __attribute__((aligned(64)));
static uint8_t flag;

#define LOOP(body, ...)                                   \
    __asm__ volatile("1:\n" body "add %0, 4\n cmp %0, %1\n jne 1b\n" __VA_ARGS__)

#define S_INC(o) "movzx ecx, byte ptr [%0+" #o "]\n inc qword ptr [%2+rcx*8]\n"
static void native_inc(const uint8_t *p, size_t n) {
    LOOP(S_INC(0) S_INC(1) S_INC(2) S_INC(3), : "+r"(p) : "r"(p + n), "r"(counts) : "rcx", "memory", "cc");
}

#define S_ADD(o) "movzx ecx, byte ptr [%0+" #o "]\n add qword ptr [%2+rcx*8], 1\n"
static void native_add(const uint8_t *p, size_t n) {
    LOOP(S_ADD(0) S_ADD(1) S_ADD(2) S_ADD(3), : "+r"(p) : "r"(p + n), "r"(counts) : "rcx", "memory", "cc");
}

#define S_SPLIT(o) "movzx ecx, byte ptr [%0+" #o "]\n mov rdx, qword ptr [%2+rcx*8]\n add rdx, 1\n mov qword ptr [%2+rcx*8], rdx\n"
static void native_split(const uint8_t *p, size_t n) {
    LOOP(S_SPLIT(0) S_SPLIT(1) S_SPLIT(2) S_SPLIT(3), : "+r"(p) : "r"(p + n), "r"(counts) : "rcx", "rdx", "memory", "cc");
}

#define S_REG(o) "movzx r11d, byte ptr [%0+" #o "]\n lea r11, [%2+r11*8]\n mov rdx, qword ptr [r11]\n add rdx, 1\n mov qword ptr [r11], rdx\n"
static void split_reg(const uint8_t *p, size_t n) {
    LOOP(S_REG(0) S_REG(1) S_REG(2) S_REG(3), : "+r"(p) : "r"(p + n), "r"(counts) : "r11", "rdx", "memory", "cc");
}

#define S_INCREG(o) "movzx ecx, byte ptr [%0+" #o "]\n lea rcx, [%2+rcx*8]\n inc qword ptr [rcx]\n"
static void inc_reg(const uint8_t *p, size_t n) {
    LOOP(S_INCREG(0) S_INCREG(1) S_INCREG(2) S_INCREG(3), : "+r"(p) : "r"(p + n), "r"(counts) : "rcx", "memory", "cc");
}

#define S_V8(o) "movzx ebx, byte ptr [%0+" #o "]\n lea ebx, [rax+rbx*8+0x2830]\n mov rdx, qword ptr [%2+rbx]\n add rdx, 1\n mov qword ptr [%2+rbx], rdx\n"
static void v8_exact(const uint8_t *p, size_t n) {
    LOOP("cmp byte ptr [%3], 0\n jne 2f\n" S_V8(0) S_V8(1) S_V8(2) S_V8(3), "2:\n" : "+r"(p) : "r"(p + n), "r"((uint8_t *)counts - 0x2830), "r"(&flag), "a"(0) : "rbx", "rdx", "memory", "cc");
}

static void v8_exact_nocheck(const uint8_t *p, size_t n) {
    LOOP(S_V8(0) S_V8(1) S_V8(2) S_V8(3), : "+r"(p) : "r"(p + n), "r"((uint8_t *)counts - 0x2830), "a"(0) : "rbx", "rdx", "memory", "cc");
}

static double now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}

static int cmp(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

typedef void (*kernel)(const uint8_t *, size_t);

int main(int argc, char **argv) {
    int value_count = argc > 1 ? atoi(argv[1]) : 1;
    uint8_t *image = aligned_alloc(64, PIXELS);
    for (size_t i = 0; i < PIXELS; i++) image[i] = (uint8_t)((i * 2654435761u >> 7) % value_count * (256 / value_count));
    struct { const char *name; kernel run; } kernels[] = {
        {"native: inc [b+i*8]", native_inc},
        {"add [b+i*8],1", native_add},
        {"load/add/store [b+i*8]", native_split},
        {"load/add/store [reg]", split_reg},
        {"inc [reg]", inc_reg},
        {"V8 exact [b+i] + check", v8_exact},
        {"V8 exact [b+i] no check", v8_exact_nocheck},
    };
    enum { REPS = 15 };
    for (int round = 0; round < 2; round++)
        for (size_t k = 0; k < sizeof kernels / sizeof *kernels; k++) {
            double t[REPS];
            for (int r = 0; r < REPS; r++) {
                memset(counts, 0, sizeof counts);
                double s = now();
                kernels[k].run(image, PIXELS);
                t[r] = now() - s;
            }
            qsort(t, REPS, sizeof *t, cmp);
            uint64_t total = 0;
            for (int b = 0; b < 256; b++) total += counts[b];
            if (round == 1)
                printf("k=%-3d %-26s median %7.2f ms  %.3f ns/pixel  %s\n", value_count, kernels[k].name,
                       t[REPS / 2] * 1e3, t[REPS / 2] * 1e9 / PIXELS, total == PIXELS ? "ok" : "BAD TOTAL");
        }
    return 0;
}
