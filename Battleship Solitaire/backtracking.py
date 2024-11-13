from constraints import *
from csp import *


def ac3(csp, var, val):
    """Combined forward checking and AC-3"""
    # Process constraints
    for constraint in csp.constraintsOf(var):
        # Handle ship placement constraints
        if val in {'<', '>', '^', 'v', 'M', 'S'} and constraint.name().startswith('NValuesConstraint_'):
            ship_count = sum(1 for v in constraint.scope() if v.getValue() in {'<', '>', '^', 'v', 'M', 'S'})
            if ship_count == int(constraint.name()[-1]):
                for uvar in (v for v in constraint.scope() if not v.isAssigned()):
                    for ship_val in [v for v in uvar.curDomain() if v != '.']:
                        uvar.pruneValue(ship_val, var, val)

        # Regular constraint processing
        for next_var in constraint.scope():
            if not next_var.isAssigned():
                for next_val in list(next_var.curDomain()):
                    if not constraint.hasSupport(next_var, next_val):
                        next_var.pruneValue(next_val, var, val)
                if next_var.curDomainSize() == 0:
                    return False
    return True


def solve_csp(csp, assignments=None):
    """Main solving function combining GAC and backtracking"""
    if assignments:
        for var, val in assignments.items():
            if not ac3(csp, var, val):
                return []

    # Get unassigned variable with smallest domain
    var = min((v for v in csp.variables() if not v.isAssigned()),
              key=lambda x: x.curDomainSize(), default=None)

    if not var:
        return [{v.name(): v.getValue() for v in csp.variables() if v.isAssigned()}]

    solutions = []
    for val in var.curDomain():
        var.setValue(val)
        if ac3(csp, var, val):
            solutions.extend(solve_csp(csp))
        var.unAssign()
        Variable.restoreValues(var, val)

    return solutions