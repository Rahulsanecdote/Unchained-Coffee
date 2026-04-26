export const MOCK_PRODUCTS = {
  "papayo-natural": {
    id: "papayo-natural-8001",
    handle: "papayo-natural",
    title: "Papayo Natural Process",
    subtitle: "by Maria del Pilar Naranjo Giron",
    producer: "Maria del Pilar Naranjo Giron",
    farm: "Los Pinos",
    region: "Tolima, Colombia",
    altitude: "1,600 masl",
    process: "Natural",
    roast: "Medium",
    ideal_for: "Pour Over",
    price: 30.00,
    image: "https://unchainedcoffee.com/cdn/shop/files/Papayo_Natural_Process_Maria_del_Pilar_Naranjo.png?v=1770848927&width=800",
    tasting_notes: ["Golden Berry", "Cantaloupe", "Peach"],
    sensory: {
      aroma: 7, flavor: 8, aftertaste: 7,
      acidity: 6, sweetness: 8, mouthfeel: 7
    },
    mouthfeel_descriptor: "Syrupy",
    variants: [
      { id: "papayo-250gr-whole", size: "250gr", grind: "Whole Bean" },
      { id: "papayo-250gr-medium", size: "250gr", grind: "Medium" },
      { id: "papayo-250gr-fine", size: "250gr", grind: "Fine" }
    ]
  },
  "geisha-honey": {
    id: "geisha-honey-8002",
    handle: "geisha-honey",
    title: "Geisha Honey Process",
    subtitle: "by Maria del Pilar Naranjo Giron",
    producer: "Maria del Pilar Naranjo Giron",
    farm: "Los Pinos",
    region: "Tolima, Colombia",
    altitude: "1,600 masl",
    process: "Honey",
    roast: "Light-Medium",
    ideal_for: "Pour Over",
    price: 35.00,
    image: "https://unchainedcoffee.com/cdn/shop/files/Geisha_Honey_Process_Maria_del_Pilar_Naranjo.png?v=1770849019&width=800",
    tasting_notes: ["Lemongrass", "Pineapple", "Starfruit"],
    sensory: {
      aroma: 8, flavor: 9, aftertaste: 8,
      acidity: 7, sweetness: 8, mouthfeel: 6
    },
    mouthfeel_descriptor: "Silky",
    variants: [
      { id: "geisha-250gr-whole", size: "250gr", grind: "Whole Bean" },
      { id: "geisha-250gr-medium", size: "250gr", grind: "Medium" },
      { id: "geisha-250gr-fine", size: "250gr", grind: "Fine" }
    ]
  },
  "red-bourbon-semi-washed": {
    id: "red-bourbon-8003",
    handle: "red-bourbon-semi-washed",
    title: "Red Bourbon Semi-Washed",
    subtitle: "by Maria del Pilar Naranjo Giron",
    producer: "Maria del Pilar Naranjo Giron",
    farm: "Los Pinos",
    region: "Tolima, Colombia",
    altitude: "1,600 masl",
    process: "Semi-Washed",
    roast: "Medium",
    ideal_for: "Espresso",
    price: 25.00,
    image: "https://unchainedcoffee.com/cdn/shop/files/Red_Bourbon_Semi_Washed_Maria_del_Pilar_Naranjo.png?v=1770849552&width=800",
    tasting_notes: ["Red Fruits", "White Chocolate", "Caramel"],
    sensory: {
      aroma: 7, flavor: 7, aftertaste: 7,
      acidity: 5, sweetness: 7, mouthfeel: 8
    },
    mouthfeel_descriptor: "Creamy",
    variants: [
      { id: "bourbon-250gr-whole", size: "250gr", grind: "Whole Bean" },
      { id: "bourbon-250gr-medium", size: "250gr", grind: "Medium" },
      { id: "bourbon-250gr-fine", size: "250gr", grind: "Fine" }
    ]
  }
};

export const CANONICAL_TAGS = [
  "Fruity", "Floral", "Citrus", "Berry", "Stone Fruit", "Tropical",
  "Chocolatey", "Nutty", "Caramel", "Spicy", "Herbal", "Earthy"
];

export const PROCESS_TAGS = [
  "Funky/Fermenty", "Boozy", "Winey", "Jammy", "Clean", "Tea-like", "Juicy", "Syrupy"
];

export const FIT_ISSUE_TAGS = [
  "Too bright", "Not sweet enough", "Too bitter", "Too heavy",
  "Too light", "Too funky", "Perfectly balanced"
];
