"""Skill graph — alias resolution and implied skill mappings."""

from __future__ import annotations

# Normalize variant skill names to canonical forms
SKILL_ALIASES: dict[str, str] = {
    "nodejs": "node.js", "node": "node.js", "node js": "node.js",
    "reactjs": "react", "react.js": "react", "react js": "react",
    "vuejs": "vue", "vue.js": "vue",
    "angularjs": "angular", "angular.js": "angular",
    "postgres": "postgresql", "pg": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes", "kube": "kubernetes",
    "tf": "tensorflow",
    "scikit": "scikit-learn", "sklearn": "scikit-learn",
    "gpt": "openai", "chatgpt": "openai",
    "llm": "large language models", "llms": "large language models",
    "js": "javascript", "es6": "javascript",
    "ts": "typescript",
    "py": "python", "python3": "python",
    "cpp": "c++", "c plus plus": "c++",
    "csharp": "c#", "c sharp": "c#",
    "aws lambda": "aws", "amazon web services": "aws",
    "google cloud": "gcp", "google cloud platform": "gcp",
    "ms azure": "azure", "microsoft azure": "azure",
    "ci cd": "ci/cd", "cicd": "ci/cd",
    "github action": "github actions", "gh actions": "github actions",
    "rest": "rest api", "restful": "rest api",
    "dl": "deep learning",
    "ml": "machine learning",
    "cv": "computer vision",
    "dsa": "data structures",
    "oop": "object oriented programming",
    "os": "operating systems",
    "db": "database", "databases": "database",
    "nextjs": "next.js", "next": "next.js",
    "nuxtjs": "nuxt.js", "nuxt": "nuxt.js",
    "expressjs": "express", "express.js": "express",
    "pytorch": "pytorch",
    "huggingface": "hugging face", "hf": "hugging face",
}

# When a resume mentions skill X, also credit these implied skills
SKILL_IMPLIES: dict[str, list[str]] = {
    "react": ["javascript", "html", "css"],
    "next.js": ["react", "javascript", "html", "css"],
    "vue": ["javascript", "html", "css"],
    "angular": ["typescript", "javascript", "html", "css"],
    "django": ["python"],
    "flask": ["python"],
    "fastapi": ["python"],
    "express": ["javascript", "node.js"],
    "pytorch": ["python", "machine learning"],
    "tensorflow": ["python", "machine learning"],
    "scikit-learn": ["python", "machine learning"],
    "keras": ["python", "deep learning"],
    "pandas": ["python", "data analysis"],
    "numpy": ["python"],
    "kubernetes": ["docker", "devops"],
    "docker": ["linux"],
    "aws": ["cloud"],
    "gcp": ["cloud"],
    "azure": ["cloud"],
    "ci/cd": ["devops"],
    "github actions": ["ci/cd", "devops"],
    "postgresql": ["sql", "database"],
    "mysql": ["sql", "database"],
    "mongodb": ["nosql", "database"],
    "redis": ["database", "caching"],
    "spark": ["big data", "data engineering"],
    "hadoop": ["big data", "data engineering"],
    "terraform": ["infrastructure as code", "devops"],
    "graphql": ["api"],
    "rest api": ["api"],
    "typescript": ["javascript"],
    "hugging face": ["machine learning", "nlp", "python"],
    "spacy": ["nlp", "python"],
    "nltk": ["nlp", "python"],
    "opencv": ["computer vision", "python"],
    "tableau": ["data visualization", "data analysis"],
    "power bi": ["data visualization", "data analysis"],
}


def normalize_skill(skill: str) -> str:
    """Normalize a skill name through the alias map."""
    lower = skill.lower().strip()
    return SKILL_ALIASES.get(lower, lower)


def get_implied_skills(skill: str) -> list[str]:
    """Get skills implied by a given skill."""
    canonical = normalize_skill(skill)
    return SKILL_IMPLIES.get(canonical, [])


def expand_skills(skills: set[str]) -> set[str]:
    """Expand a set of skills with their implied skills."""
    expanded = set()
    for skill in skills:
        canonical = normalize_skill(skill)
        expanded.add(canonical)
        for implied in get_implied_skills(canonical):
            expanded.add(implied)
    return expanded
