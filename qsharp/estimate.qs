namespace ResourceLandscape {
    open Microsoft.Quantum.Intrinsic;
    
    /// <summary>
    /// Resource estimator pipeline is driven from Python.
    /// This is a stub operation that can be compiled and used as a placeholder.
    /// </summary>
    operation EstimateStub() : Unit {
        Message("Resource estimator pipeline is driven from Python.");
        using (q = Qubit()) {
            H(q);
            Reset(q);
        }
    }
}
