"""Original text for BaZi (Chinese Four Pillars), houses, Saturn/Jupiter signs and timing."""

STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
BRANCHES = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
STEM_ELEMENT = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]
BRANCH_ELEMENT = ["Water", "Earth", "Wood", "Wood", "Earth", "Fire", "Fire", "Earth", "Metal", "Metal", "Earth", "Water"]

# Day Master (the day stem is "you" in BaZi)
DAY_MASTER = {
"Yang Wood": ("The Great Tree", "Upright, growth-minded and principled. You grow steadily toward your goals and stand firm in what you believe; you can be inflexible when challenged."),
"Yin Wood": ("The Vine and Flower", "Flexible, gentle and resourceful. You reach your goals by adapting and cooperating, and you read people well; you can lose your own direction when pressured."),
"Yang Fire": ("The Sun", "Warm, open and generous. You bring light and enthusiasm to a room and want to be seen; you can burn out or overextend."),
"Yin Fire": ("The Candle", "Focused, perceptive and quietly warm. You light up a small circle intensely and notice what others miss; you can be sensitive and slow to forgive."),
"Yang Earth": ("The Mountain", "Stable, dependable and protective. People lean on you and you rarely rush; you can be stubborn and slow to change."),
"Yin Earth": ("The Garden Soil", "Nurturing, practical and receptive. You help things grow and absorb a lot from others; you can worry and take on too much."),
"Yang Metal": ("The Sword", "Direct, decisive and just. You cut through confusion and defend what matters; you can be blunt or harsh."),
"Yin Metal": ("The Jewel", "Refined, discerning and sensitive to quality. You care about beauty, standards and being valued; you can be self-critical and guarded."),
"Yang Water": ("The Ocean", "Expansive, adaptable and far-seeing. You move toward wide horizons and connect many things; you can be restless or hard to pin down."),
"Yin Water": ("The Rain and Mist", "Intuitive, subtle and imaginative. You sense currents beneath the surface and work around obstacles; you can doubt yourself and drift."),
}

ANIMAL_TEXT = {
"Rat": "Resourceful, quick and observant; an instinct for opportunity and survival.",
"Ox": "Patient, dependable and hardworking; slow, steady progress and strong principles.",
"Tiger": "Brave, spirited and independent; a natural challenger with a streak of the dramatic.",
"Rabbit": "Gentle, diplomatic and tasteful; peace-seeking with a sharp eye for people.",
"Dragon": "Confident, charismatic and ambitious; big ideas and a strong presence.",
"Snake": "Intuitive, private and strategic; deep thinking and quiet determination.",
"Horse": "Energetic, free-spirited and sociable; a need for movement, independence and variety.",
"Goat": "Gentle, artistic and empathetic; sensitive to atmosphere and in need of security.",
"Monkey": "Clever, playful and inventive; quick problem-solving and a love of novelty.",
"Rooster": "Meticulous, candid and hardworking; proud of standards and presentation.",
"Dog": "Loyal, honest and protective; a strong sense of justice and a faithful friend.",
"Pig": "Generous, warm and sincere; enjoys life and trusts easily.",
}

ELEMENT_BALANCE = {
"Wood": dict(dom="Wood is abundant in your Four Pillars: growth, planning and drive for expansion. Watch for impatience and overreaching.",
             low="Wood is scarce: you may need to deliberately cultivate vision, flexibility and a sense of growth."),
"Fire": dict(dom="Fire is abundant: passion, enthusiasm and expressiveness. Watch for burnout and impulsiveness.",
             low="Fire is scarce: warmth, joy and visibility may need conscious effort."),
"Earth": dict(dom="Earth is abundant: stability, reliability and caution. Watch for stubbornness and worry.",
              low="Earth is scarce: grounding routines, patience and follow-through may need conscious effort."),
"Metal": dict(dom="Metal is abundant: structure, precision and standards. Watch for rigidity and harsh self-judgement.",
              low="Metal is scarce: boundaries, discipline and finishing may need conscious effort."),
"Water": dict(dom="Water is abundant: intuition, adaptability and depth. Watch for overthinking and drifting.",
              low="Water is scarce: reflection, rest and emotional flow may need conscious effort."),
}

# earthly-branch relationships (BaZi compatibility)
SIX_HARMONY = {frozenset(p) for p in [("Rat", "Ox"), ("Tiger", "Pig"), ("Rabbit", "Dog"), ("Dragon", "Rooster"), ("Snake", "Monkey"), ("Horse", "Goat")]}
TRINES = [{"Rat", "Dragon", "Monkey"}, {"Ox", "Snake", "Rooster"}, {"Tiger", "Horse", "Dog"}, {"Rabbit", "Goat", "Pig"}]
CLASHES = {frozenset((ANIMALS[i], ANIMALS[(i + 6) % 12])) for i in range(6)}

# ---- houses -------------------------------------------------------------------------------
HOUSE_NAME = ["Self", "Money & values", "Communication & learning", "Home & roots", "Creativity & romance", "Work & daily habits",
              "Partnership", "Intimacy & shared resources", "Beliefs & horizons", "Career & reputation", "Friends & hopes", "Rest & the unseen"]
HOUSE_THEME = [
    "identity, appearance and the way you begin things",
    "income, possessions and what you value",
    "everyday communication, siblings, short journeys and learning",
    "home, family and your emotional foundations",
    "creativity, romance, play and self-expression",
    "daily routines, work habits, service and wellbeing habits",
    "committed partnerships, in love and in business",
    "deep intimacy, shared money and personal transformation",
    "beliefs, travel, higher learning and the search for meaning",
    "career, public role and reputation",
    "friendships, communities and long-term hopes",
    "solitude, rest, intuition and what is hidden",
]
PLANET_HOUSE_LEAD = {
    "Sun": ("Where you shine", "this is where you want to shine and be recognised"),
    "Moon": ("Where you feel at home", "this is where you feel emotionally at home, and most reactive"),
    "Venus": ("Where you find love and pleasure", "this is where you look for love, beauty and enjoyment"),
    "Mars": ("Where you spend your energy", "this is where you put your drive and fight your battles"),
    "Jupiter": ("Where growth arrives", "this is where growth, opportunity and good fortune tend to come"),
    "Saturn": ("Where you build slowly", "this is where you build slowly, and where life tests you into mastery"),
}
ORD = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"  # noqa: E731

# ---- Saturn / Jupiter by sign ---------------------------------------------------------------
JUPITER_SIGN = {
"Aries": "growth through courage, initiative and self-trust", "Taurus": "growth through patience, resources and steady building",
"Gemini": "growth through learning, conversation and connections", "Cancer": "growth through family, caring and emotional security",
"Leo": "growth through creativity, generosity and leadership", "Virgo": "growth through skill, service and practical improvement",
"Libra": "growth through partnership, fairness and collaboration", "Scorpio": "growth through depth, trust and transformation",
"Sagittarius": "growth through travel, teaching and belief", "Capricorn": "growth through discipline, responsibility and achievement",
"Aquarius": "growth through community, originality and shared ideals", "Pisces": "growth through compassion, imagination and faith",
}
SATURN_SIGN = {
"Aries": "lessons in patience, self-control and finishing what you start", "Taurus": "lessons in security, self-worth and letting go of what no longer serves",
"Gemini": "lessons in focus, disciplined thinking and honest speech", "Cancer": "lessons in emotional self-reliance and building your own sense of home",
"Leo": "lessons in confidence without pride and creating on your own terms", "Virgo": "lessons in letting go of perfectionism and trusting your skills",
"Libra": "lessons in commitment, fairness and being a true equal in partnership", "Scorpio": "lessons in trust, control and facing what you avoid",
"Sagittarius": "lessons in grounding your beliefs and sticking with big plans", "Capricorn": "lessons in authority, ambition and balancing work with being human",
"Aquarius": "lessons in belonging, responsibility to groups and staying open to change", "Pisces": "lessons in boundaries, practical faith and separating compassion from rescue",
}
YEAR_LORD = {
"Sun": "Sun: a year about identity, visibility and purpose.", "Moon": "Moon: a year about emotions, home and the people close to you.",
"Mercury": "Mercury: a year about learning, communication, work and decisions.", "Venus": "Venus: a year about relationships, values, comfort and creativity.",
"Mars": "Mars: a year about action, energy and asserting yourself.", "Jupiter": "Jupiter: a year about growth, opportunity and widening your world.",
"Saturn": "Saturn: a year about responsibility, structure and earning your results.",
}
