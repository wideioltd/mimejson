This directory contains test design to exercise the code to ensure
that all branches are used - and that they provide the expected output
and the expected side effects (mock).

Unit tests must be as much small, transversal and implementation
independent.
- Small (they only describe input, expected output, expected side effect)
- They dont't require documentation
- Transversal implies that the input must be defined for all models
  and that the unit tests are going to be applied for all these inputs
- Whenever possible expected outputs and side-effect must be extracted from code by reflexion

In our definition are not to be minimal but shall encompass all
subelements of code required for the code to work. Mocking must be
limited to side effects.
