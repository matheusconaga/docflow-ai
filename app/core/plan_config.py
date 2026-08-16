# Centraliza os limites de planos do EducAssist para uso em toda a aplicação.
# Ao alterar aqui, todos os routes que importam este módulo serão atualizados.

PLAN_LIMITS = {
    "free": {
        "classes": 1,
        "credits": 10,
        "docs": 5,
        "name": "Gratuito",
    },
    "essencial": {
        "classes": 5,
        "credits": 80,
        "docs": 9999,  # Ilimitado
        "name": "Essencial",
    },
    "pro": {
        "classes": 9999,  # Ilimitado
        "credits": 240,
        "docs": 9999,  # Ilimitado
        "name": "Pro",
    },
}


def get_class_limit(plan_type: str) -> int:
    return PLAN_LIMITS.get(plan_type, PLAN_LIMITS["free"])["classes"]


def get_credit_limit(plan_type: str) -> int:
    return PLAN_LIMITS.get(plan_type, PLAN_LIMITS["free"])["credits"]
