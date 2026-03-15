
export const getDriverImage = (name) => {
  if (!name) return '';
  const normalized = name.toLowerCase().trim();
  
  // Mapping for FastF1 short names / Full names to NEW local file names
  const mapper = {
    'g russell': 'George_Russell_63.png',
    'george russell': 'George_Russell_63.png',
    'l norris': 'Lando_Norris_1.png',
    'lando norris': 'Lando_Norris_1.png',
    'm verstappen': 'Max_Verstappen_3.png',
    'max verstappen': 'Max_Verstappen_3.png',
    'k antonelli': 'Kimi_Antonelli_12.png',
    'kimi antonelli': 'Kimi_Antonelli_12.png',
    'andrea kimi antonelli': 'Kimi_Antonelli_12.png',
    'c leclerc': 'Charles_Leclerc_16.png',
    'charles leclerc': 'Charles_Leclerc_16.png',
    'l hamilton': 'Lewis_Hamilton_44.png',
    'lewis hamilton': 'Lewis_Hamilton_44.png',
    'o bearman': 'Oliver_Bearman_87.png',
    'oliver bearman': 'Oliver_Bearman_87.png',
    'a lindblad': 'Arvid_Lindblad_41.png',
    'arvid lindblad': 'Arvid_Lindblad_41.png',
    'g bortoleto': 'Gabriel_Bortoleto_5.png',
    'gabriel bortoleto': 'Gabriel_Bortoleto_5.png',
    'p gasly': 'Pierre_Gasly_10.png',
    'pierre gasly': 'Pierre_Gasly_10.png',
    'e ocon': 'Esteban_Ocon_31.png',
    'esteban ocon': 'Esteban_Ocon_31.png',
    'a albon': 'Alexander_Albon_23.png',
    'alex albon': 'Alexander_Albon_23.png',
    'alexander albon': 'Alexander_Albon_23.png',
    'l lawson': 'Liam_Lawson_30.png',
    'liam lawson': 'Liam_Lawson_30.png',
    'f colapinto': 'Franco_Colapinto_43.png',
    'franco colapinto': 'Franco_Colapinto_43.png',
    'c sainz': 'Carlos_Sainz_55.png',
    'carlos sainz': 'Carlos_Sainz_55.png',
    's perez': 'Sergio_Perez_11.png',
    'sergio perez': 'Sergio_Perez_11.png',
    'sergio pérez': 'Sergio_Perez_11.png',
    'l stroll': 'Lance_Stroll_18.png',
    'lance stroll': 'Lance_Stroll_18.png',
    'f alonso': 'Fernando_Alonso_14.png',
    'fernando alonso': 'Fernando_Alonso_14.png',
    'v bottas': 'Valtteri_Bottas_77.png',
    'valtteri bottas': 'Valtteri_Bottas_77.png',
    'i hadjar': 'Isack_Hadjar_6.png',
    'isack hadjar': 'Isack_Hadjar_6.png',
    'o piastri': 'Oscar_Piastri_81.png',
    'oscar piastri': 'Oscar_Piastri_81.png',
    'n hulkenberg': 'Nico_Hulkenberg_27.png',
    'nico hulkenberg': 'Nico_Hulkenberg_27.png',
    'nico hülkenberg': 'Nico_Hulkenberg_27.png'
  };

  const fileName = mapper[normalized];
  if (fileName) {
    return `/assets/drivers/${fileName}`;
  }
  
  // Fallback
  const fallback = normalized.replace(/ /g, '_');
  return `/assets/drivers/${fallback}.png`;
};

export const getTeamImage = (name) => {
  if (!name) return '';
  const normalized = name.toLowerCase().trim();
  
  const mapper = {
    'mercedes': 'mercedes-amg-petronas',
    'mercedes-amg petronas': 'mercedes-amg-petronas',
    'mercedes-amg petronas formula one team': 'mercedes-amg-petronas',
    'mclaren': 'mclaren-f1-team',
    'mclaren mercedes': 'mclaren-f1-team',
    'mclaren formula 1 team': 'mclaren-f1-team',
    'mclaren f1 team': 'mclaren-f1-team',
    'red bull': 'oracle-red-bull-racing',
    'red bull racing': 'oracle-red-bull-racing',
    'oracle red bull racing': 'oracle-red-bull-racing',
    'red bull racing red bull ford': 'oracle-red-bull-racing',
    'ferrari': 'scuderia-ferrari',
    'scuderia ferrari': 'scuderia-ferrari',
    'scuderia ferrari hp': 'scuderia-ferrari',
    'aston martin': 'aston-martin-aramco',
    'aston martin honda': 'aston-martin-aramco',
    'aston martin aramco': 'aston-martin-aramco',
    'aston martin aramco formula one team': 'aston-martin-aramco',
    'alpine': 'bwt-alpine-f1-team',
    'bwt alpine': 'bwt-alpine-f1-team',
    'alpine mercedes': 'bwt-alpine-f1-team',
    'bwt alpine f1 team': 'bwt-alpine-f1-team',
    'bwt alpine formula one team': 'bwt-alpine-f1-team',
    'williams': 'williams-racing',
    'williams mercedes': 'williams-racing',
    'williams racing': 'williams-racing',
    'atlassian williams racing': 'williams-racing',
    'haas': 'moneygram-haas-f1',
    'haas ferrari': 'moneygram-haas-f1',
    'haas f1 team': 'moneygram-haas-f1',
    'moneygram haas f1 team': 'moneygram-haas-f1',
    'moneygram haas f1': 'moneygram-haas-f1',
    'racing bulls': 'racing-bulls',
    'racing bulls red bull ford': 'racing-bulls',
    'visa cash app racing bulls': 'racing-bulls',
    'rb': 'racing-bulls',
    'audi': 'audi-f1-team',
    'audi f1 team': 'audi-f1-team',
    'sauber': 'audi-f1-team',
    'kick sauber': 'audi-f1-team',
    'stake f1 team kick sauber': 'audi-f1-team',
    'cadillac': 'cadillac-f1',
    'cadillac ferrari': 'cadillac-f1',
    'cadillac f1 team': 'cadillac-f1',
    'andretti': 'cadillac-f1',
    'andretti cadillac': 'cadillac-f1'
  };

  const fileName = mapper[normalized] || normalized.replace(/ /g, '-');
  return `/assets/teams/${fileName}.png`;
};

export const getCircuitImage = (circuitName) => {
  if (!circuitName) return '';
  const normalized = circuitName.toLowerCase().trim();
  
  const mapper = {
    'albert park, melbourne': 'Australia_Albert_Park',
    'melbourne': 'Australia_Albert_Park',
    'shanghai international': 'China_Shanghai_International',
    'shanghai': 'China_Shanghai_International',
    'suzuka': 'Japan_Suzuka',
    'sakhir': 'Bahrain_Bahrain_International',
    'jeddah corniche': 'Saudi_Arabia_Jeddah_Corniche',
    'jeddah': 'Saudi_Arabia_Jeddah_Corniche',
    'miami international': 'USA_Miami_International',
    'miami': 'USA_Miami_International',
    'circuit gilles-villeneuve': 'Canada_Gilles_Villeneuve',
    'montreal': 'Canada_Gilles_Villeneuve',
    'circuit de monaco': 'Monaco_Circuit_de_Monaco',
    'monaco': 'Monaco_Circuit_de_Monaco',
    'barcelona-catalunya': 'Spain_Barcelona_Catalunya',
    'barcelona': 'Spain_Barcelona_Catalunya',
    'red bull ring': 'Austria_Red_Bull_Ring',
    'spielberg': 'Austria_Red_Bull_Ring',
    'silverstone': 'Great_Britain_Silverstone',
    'spa-francorchamps': 'Belgium_Spa_Francorchamps',
    'spa': 'Belgium_Spa_Francorchamps',
    'hungaroring': 'Hungary_Hungaroring',
    'budapest': 'Hungary_Hungaroring',
    'zandvoort': 'Netherlands_Zandvoort',
    'monza': 'Italy_Monza',
    'madrid street circuit': 'Madrid_Street_Circuit', // Fallback if added later
    'madrid': 'Madrid_Street_Circuit',
    'baku city circuit': 'Azerbaijan_Baku',
    'baku': 'Azerbaijan_Baku',
    'marina bay': 'Singapore_Marina_Bay_Street',
    'singapore': 'Singapore_Marina_Bay_Street',
    'cota, austin': 'USA_Circuit_of_the_Americas',
    'austin': 'USA_Circuit_of_the_Americas',
    'autodromo hermanos rodriguez': 'Mexico_Hermanos_Rodriguez',
    'mexico city': 'Mexico_Hermanos_Rodriguez',
    'interlagos, s\u00e3o paulo': 'Brazil_Jose_Carlos_Pace',
    's\u00e3o paulo': 'Brazil_Jose_Carlos_Pace',
    'las vegas strip': 'USA_Las_Vegas_Strip',
    'las vegas': 'USA_Las_Vegas_Strip',
    'lusail international': 'Qatar_Lusail_International',
    'lusail': 'Qatar_Lusail_International',
    'yas marina': 'UAE_Abu_Dhabi_Yas_Marina',
    'abu dhabi': 'UAE_Abu_Dhabi_Yas_Marina'
  };

  const fileName = mapper[normalized] || normalized.replace(/[^a-z0-9]/g, '_');
  return `/assets/circuits/${fileName}.png`;
};
