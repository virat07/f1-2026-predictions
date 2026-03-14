
export const getDriverImage = (name) => {
  if (!name) return '';
  const normalized = name.toLowerCase().trim();
  
  // Mapping for FastF1 short names to local file names
  // Add entries as needed based on ml-predictions.json
  const mapper = {
    'g russell': 'george-russell',
    'l norris': 'lando-norris',
    'm verstappen': 'max-verstappen',
    'k antonelli': 'andrea-kimi-antonelli',
    'c leclerc': 'charles-leclerc',
    'l hamilton': 'lewis-hamilton',
    'o bearman': 'oliver-bearman',
    'a lindblad': 'arvid-lindblad',
    'g bortoleto': 'gabriel-bortoleto',
    'p gasly': 'pierre-gasly',
    'e ocon': 'esteban-ocon',
    'a albon': 'alexander-albon',
    'l lawson': 'liam-lawson',
    'f colapinto': 'franco-colapinto',
    'c sainz': 'carlos-sainz',
    's perez': 'sergio-perez',
    'l stroll': 'lance-stroll',
    'f alonso': 'fernando-alonso',
    'v bottas': 'valtteri-bottas',
    'i hadjar': 'isack-hadjar',
    'o piastri': 'oscar-piastri',
    'n hulkenberg': 'nico-hulkenberg'
  };

  const fileName = mapper[normalized] || normalized.replace(/ /g, '-');
  return `/assets/drivers/${fileName}.png`;
};

export const getTeamImage = (name) => {
  if (!name) return '';
  const normalized = name.toLowerCase().trim();
  
  const mapper = {
    'mercedes': 'mercedes-amg-petronas',
    'mclaren': 'mclaren-f1-team',
    'red bull': 'oracle-red-bull-racing',
    'red bull racing': 'oracle-red-bull-racing',
    'ferrari': 'scuderia-ferrari',
    'scuderia ferrari': 'scuderia-ferrari',
    'aston martin': 'aston-martin-aramco',
    'alpine': 'bwt-alpine-f1-team',
    'williams': 'williams-racing',
    'haas': 'moneygram-haas-f1',
    'haas f1 team': 'moneygram-haas-f1',
    'racing bulls': 'racing-bulls',
    'audi': 'audi-f1-team',
    'cadillac': 'cadillac-f1'
  };

  const fileName = mapper[normalized] || normalized.replace(/ /g, '-');
  return `/assets/teams/${fileName}.png`;
};

export const getCircuitImage = (circuitName) => {
  if (!circuitName) return '';
  const normalized = circuitName.toLowerCase().trim();
  
  const mapper = {
    'albert park, melbourne': 'albert_park',
    'shanghai international': 'shanghai',
    'suzuka': 'suzuka',
    'sakhir': 'bahrain',
    'jeddah corniche': 'jeddah',
    'miami international': 'miami',
    'circuit gilles-villeneuve': 'montreal',
    'circuit de monaco': 'monaco',
    'barcelona-catalunya': 'barcelona',
    'red bull ring': 'austria',
    'silverstone': 'silverstone',
    'spa-francorchamps': 'spa',
    'hungaroring': 'hungaroring',
    'zandvoort': 'zandvoort',
    'monza': 'monza',
    'madrid street circuit': 'madrid',
    'baku city circuit': 'baku',
    'marina bay': 'singapore',
    'cota, austin': 'austin',
    'autodromo hermanos rodriguez': 'mexico',
    'interlagos, s\u00e3o paulo': 'brazil',
    'las vegas strip': 'las_vegas',
    'lusail international': 'qatar',
    'yas marina': 'abu_dhabi'
  };

  const fileName = mapper[normalized] || normalized.replace(/[^a-z0-9]/g, '-');
  return `/assets/circuits/${fileName}.webp`;
};
