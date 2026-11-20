use super::Passes;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MeasurementPlan {
    pub(super) warmup: usize,
    pub(super) measured: usize,
    pub(super) passes: Passes,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PlanError {
    NoMeasuredIterations,
}

impl MeasurementPlan {
    pub fn new(warmup: usize, measured: usize) -> Result<Self, PlanError> {
        if measured == 0 {
            return Err(PlanError::NoMeasuredIterations);
        }
        Ok(Self {
            warmup,
            measured,
            passes: Passes::ONE,
        })
    }

    pub fn with_passes(self, passes: Passes) -> Self {
        Self { passes, ..self }
    }

    pub fn warmup(self) -> usize {
        self.warmup
    }

    pub fn measured(self) -> usize {
        self.measured
    }

    pub fn passes(self) -> Passes {
        self.passes
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn plan_requires_at_least_one_measured_iteration() {
        assert_eq!(
            MeasurementPlan::new(3, 0),
            Err(PlanError::NoMeasuredIterations)
        );
        assert!(MeasurementPlan::new(0, 1).is_ok());
    }

    #[test]
    fn plan_runs_one_pass_unless_told_otherwise() {
        let plan = MeasurementPlan::new(1, 1).unwrap();
        assert_eq!(plan.passes, Passes::ONE);
        let three = Passes::new(3).unwrap();
        assert_eq!(plan.with_passes(three).passes, three);
    }
}
