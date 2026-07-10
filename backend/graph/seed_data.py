"""Seed data for the startup ecosystem knowledge graph."""

from backend.graph.knowledge_graph import knowledge_graph


def seed_knowledge_graph() -> None:
    """Populate the knowledge graph with sample startup ecosystem data."""

    # Startups
    startups = [
        ("OpenAI", "startup", {"founded": 2015, "category": "AI", "valuation": "$80B"}),
        ("Stripe", "startup", {"founded": 2010, "category": "Fintech", "valuation": "$65B"}),
        ("Notion", "startup", {"founded": 2016, "category": "Productivity", "valuation": "$10B"}),
        ("Figma", "startup", {"founded": 2012, "category": "Design Tools", "status": "acquired"}),
        ("Linear", "startup", {"founded": 2019, "category": "Project Management", "valuation": "$1B"}),
        ("Vercel", "startup", {"founded": 2020, "category": "Cloud/Developer Tools", "valuation": "$3.5B"}),
        ("Supabase", "startup", {"founded": 2020, "category": "Backend-as-a-Service", "valuation": "$2B"}),
        ("Anthropic", "startup", {"founded": 2021, "category": "AI Safety", "valuation": "$18B"}),
        ("Databricks", "startup", {"founded": 2013, "category": "Data/AI", "valuation": "$43B"}),
        ("Canva", "startup", {"founded": 2013, "category": "Design", "valuation": "$26B"}),
    ]

    # Investors
    investors = [
        ("Sequoia Capital", "investor", {"category": "VC", "aum": "$85B"}),
        ("Andreessen Horowitz", "investor", {"category": "VC", "aum": "$35B"}),
        ("Y Combinator", "investor", {"category": "Accelerator", "companies_funded": 4000}),
        ("Founders Fund", "investor", {"category": "VC", "aum": "$11B"}),
        ("Accel", "investor", {"category": "VC", "aum": "$88B"}),
    ]

    # Markets
    markets = [
        ("AI/ML", "market", {"tam": "$1.8T", "growth_rate": "37%"}),
        ("Fintech", "market", {"tam": "$310B", "growth_rate": "20%"}),
        ("SaaS", "market", {"tam": "$720B", "growth_rate": "18%"}),
        ("Developer Tools", "market", {"tam": "$45B", "growth_rate": "25%"}),
    ]

    # Technologies
    technologies = [
        ("Python", "technology", {"category": "Language", "use": "AI/ML, Backend"}),
        ("React", "technology", {"category": "Framework", "use": "Frontend"}),
        ("FastAPI", "technology", {"category": "Framework", "use": "Backend"}),
        ("LangGraph", "technology", {"category": "Framework", "use": "AI Agents"}),
        ("ChromaDB", "technology", {"category": "Database", "use": "Vector Search"}),
        ("Next.js", "technology", {"category": "Framework", "use": "Frontend"}),
    ]

    # Add all entities
    startup_ids = {}
    for name, etype, props in startups:
        startup_ids[name] = knowledge_graph.add_entity(etype, name, props)

    investor_ids = {}
    for name, etype, props in investors:
        investor_ids[name] = knowledge_graph.add_entity(etype, name, props)

    market_ids = {}
    for name, etype, props in markets:
        market_ids[name] = knowledge_graph.add_entity(etype, name, props)

    tech_ids = {}
    for name, etype, props in technologies:
        tech_ids[name] = knowledge_graph.add_entity(etype, name, props)

    # Add relations (investor → startup)
    relations = [
        (investor_ids["Sequoia Capital"], startup_ids["OpenAI"], "invested_in", {"stage": "Series A"}),
        (investor_ids["Andreessen Horowitz"], startup_ids["Anthropic"], "invested_in", {"stage": "Series B"}),
        (investor_ids["Y Combinator"], startup_ids["Stripe"], "invested_in", {"stage": "Seed"}),
        (investor_ids["Y Combinator"], startup_ids["Notion"], "invested_in", {"stage": "Seed"}),
        (investor_ids["Founders Fund"], startup_ids["Stripe"], "invested_in", {"stage": "Series A"}),
        (investor_ids["Accel"], startup_ids["Canva"], "invested_in", {"stage": "Series A"}),
        (startup_ids["OpenAI"], market_ids["AI/ML"], "operates_in"),
        (startup_ids["Anthropic"], market_ids["AI/ML"], "operates_in"),
        (startup_ids["Stripe"], market_ids["Fintech"], "operates_in"),
        (startup_ids["Notion"], market_ids["SaaS"], "operates_in"),
        (startup_ids["Linear"], market_ids["SaaS"], "operates_in"),
        (startup_ids["Vercel"], market_ids["Developer Tools"], "operates_in"),
        (startup_ids["Supabase"], market_ids["Developer Tools"], "operates_in"),
        (startup_ids["OpenAI"], tech_ids["Python"], "uses_tech"),
        (startup_ids["Vercel"], tech_ids["React"], "uses_tech"),
        (startup_ids["Vercel"], tech_ids["Next.js"], "uses_tech"),
        (startup_ids["OpenAI"], tech_ids["LangGraph"], "uses_tech"),
    ]

    for source, target, rel_type, *rest in relations:
        props = rest[0] if rest else {}
        knowledge_graph.add_relation(source, target, rel_type, props)

    print(f"Seeded knowledge graph: {len(startup_ids)} startups, {len(investor_ids)} investors, {len(relations)} relations")