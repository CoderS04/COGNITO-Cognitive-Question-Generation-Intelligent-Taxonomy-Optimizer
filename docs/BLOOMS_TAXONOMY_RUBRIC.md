# Bloom's Taxonomy Cognitive Classification Rubric & Specification

## 1. Overview
In accordance with Bloom's Revised Taxonomy (Anderson & Krathwohl, 2001), educational assessments within **COGNITO** are classified into six hierarchical cognitive domains (L1 through L6). Each level measures progressive cognitive complexity:

| Level | Cognitive Domain | Core Action | Typical Verbs | Marks Range (Typical) |
|---|---|---|---|---|
| **L1** | **Remember** | Retrieve relevant knowledge from long-term memory | *Define, List, State, Recall, Identify, Name, Enumerate, Mention* | 1 - 2 Marks |
| **L2** | **Understand** | Construct meaning from instructional messages | *Explain, Describe, Discuss, Summarize, Classify, Interpret, Paraphrase* | 2 - 5 Marks |
| **L3** | **Apply** | Carry out or use a procedure in a given situation | *Calculate, Apply, Solve, Demonstrate, Execute, Implement, Compute* | 5 - 8 Marks |
| **L4** | **Analyze** | Break material into constituent parts and determine relationships | *Analyze, Compare, Contrast, Differentiate, Distinguish, Deconstruct* | 6 - 10 Marks |
| **L5** | **Evaluate** | Make judgments based on criteria and standards | *Evaluate, Justify, Criticize, Defend, Validate, Appraise, Assess* | 8 - 12 Marks |
| **L6** | **Create** | Put elements together to form a coherent whole or novel structure | *Design, Formulate, Construct, Devise, Synthesize, Architect, Propose* | 10 - 15 Marks |

---

## 2. Multi-Dimensional Classification Heuristic
COGNITO utilizes a hybrid evaluation pipeline combining:
1. **Verb Anchor Matching**: Scanning for high-confidence Bloom's action verbs.
2. **Syntactic & Structural Modifiers**:
   - Conditionals (*"Given the constraint that..."*, *"Under network failure..."*) elevate cognitive demand.
   - Comparative conjunctions (*"versus"*, *"in contrast to"*, *"trade-offs between"*) push towards L4/L5.
   - Synthesis directives (*"Design a fault-tolerant architecture"*, *"Propose a novel algorithm"*) classify into L6.
3. **Contextual Semantic Embeddings**:
   - Cosine similarity matching against pre-computed exemplar anchors for each taxonomy tier.

---

## 3. Cognitive Reframing Guidelines
COGNITO provides an automated reframing engine that transforms lower-order questions (L1/L2) into higher-order inquiries (L3-L6):

- **Original (L1 Remember)**: *"Define Deadlock in Operating Systems."*
  - **Reframed (L4 Analyze)**: *"Analyze a scenario with 3 processes sharing 2 identical resource units to determine if a deadlock condition can occur."*
  - **Reframed (L6 Create)**: *"Design a deadlock-avoidance resource allocation protocol for a distributed multi-core system."*

- **Original (L2 Understand)**: *"Explain Dijkstra's algorithm for finding shortest paths."*
  - **Reframed (L3 Apply)**: *"Given a weighted graph representing network routers with negative edge detection, execute Dijkstra's algorithm to identify the optimal routing path."*
  - **Reframed (L5 Evaluate)**: *"Critique the performance and convergence of Dijkstra's algorithm compared to the Bellman-Ford algorithm on dense graphs with dynamic link weights."*
