from plantassistant.app.schemes.constants import RuleMethod


MinimumTemp = RuleMethod(
    name="core.MinimumTemp",
    sensor="temperature",
    operator=">=",
    arguments=["value", "unit"]
)

AboveFreezing = RuleMethod(
    name="core.AboveFreezing",
    description="Minimum temperature",
    sensor="temperature",
    operator=">=",
    arguments=["value", "unit"]
)