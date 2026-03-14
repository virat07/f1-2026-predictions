// Driver Championship Predictions Data
export const podiumDrivers = [
  {
    position: 1,
    name: 'Lewis Hamilton',
    number: 44,
    team: 'Ferrari',
    teamClass: 'ferrari',
    points: 421,
    gradient: 'linear-gradient(135deg, #e8002d, #7c0a02)',
    note: 'The GOAT claims his 8th title. Ferrari\'s new PU is a masterpiece.',
  },
  {
    position: 2,
    name: 'Max Verstappen',
    number: 1,
    team: 'Red Bull Racing',
    teamClass: 'redbull',
    points: 392,
    gradient: 'linear-gradient(135deg, #3671C6, #1B2A4A)',
    note: 'The reigning champion pushes hard with his new teammate but Ferrari\'s pace is relentless.',
  },
  {
    position: 3,
    name: 'Charles Leclerc',
    number: 16,
    team: 'Ferrari',
    teamClass: 'ferrari',
    points: 375,
    gradient: 'linear-gradient(135deg, #e8002d, #7c0a02)',
    note: 'Pushes Hamilton all season but narrowly misses out on the crown.',
  },
]

export const restOfGrid = [
  { pos: 4, number: 4, color: '#ff8000', name: 'Lando Norris', team: 'McLaren', points: 348 },
  { pos: 5, number: 81, color: '#ff8000', name: 'Oscar Piastri', team: 'McLaren', points: 310 },
  { pos: 6, number: 63, color: '#27f4d2', name: 'George Russell', team: 'Mercedes', points: 285 },
  { pos: 7, number: 12, color: '#27f4d2', name: 'Andrea Kimi Antonelli', team: 'Mercedes', points: 240 },
  { pos: 8, number: 14, color: '#229971', name: 'Fernando Alonso', team: 'Aston Martin', points: 168 },
  { pos: 9, number: 18, color: '#229971', name: 'Lance Stroll', team: 'Aston Martin', points: 142 },
  { pos: 10, number: 6, color: '#6692ff', name: 'Isack Hadjar', team: 'Red Bull Racing', points: 130 },
  { pos: 11, number: 10, color: '#52e252', name: 'Pierre Gasly', team: 'Alpine', points: 98 },
  { pos: 12, number: 43, color: '#52e252', name: 'Franco Colapinto', team: 'Alpine', points: 72 },
  { pos: 13, number: 27, color: '#b6babd', name: 'Nico Hülkenberg', team: 'Audi', points: 65 },
  { pos: 14, number: 5, color: '#b6babd', name: 'Gabriel Bortoleto', team: 'Audi', points: 48 },
  { pos: 15, number: 23, color: '#64c4ff', name: 'Alex Albon', team: 'Williams', points: 40 },
  { pos: 16, number: 55, color: '#64c4ff', name: 'Carlos Sainz', team: 'Williams', points: 35 },
  { pos: 17, number: 87, color: '#2293d1', name: 'Oliver Bearman', team: 'Haas', points: 28 },
  { pos: 18, number: 31, color: '#2293d1', name: 'Esteban Ocon', team: 'Haas', points: 22 },
  { pos: 19, number: 30, color: '#1e6176', name: 'Liam Lawson', team: 'Racing Bulls', points: 15 },
  { pos: 20, number: 41, color: '#1e6176', name: 'Arvid Lindblad', team: 'Racing Bulls', points: 10 },
  { pos: 21, number: 77, color: '#C0C0C0', name: 'Valtteri Bottas', team: 'Cadillac', points: 8 },
  { pos: 22, number: 11, color: '#C0C0C0', name: 'Sergio Pérez', team: 'Cadillac', points: 5 },
]

// Constructor Championship Predictions Data
export const constructors = [
  { rank: 1, name: 'Scuderia Ferrari', drivers: 'Hamilton · Leclerc', points: 796, color: '#e8002d', note: 'The Prancing Horse masters the new PU formula. Hamilton and Leclerc form the most feared pairing on the grid.' },
  { rank: 2, name: 'McLaren F1 Team', drivers: 'Norris · Piastri', points: 658, color: '#ff8000', note: 'McLaren\'s momentum carries forward. Papaya remains a championship contender.' },
  { rank: 3, name: 'Oracle Red Bull Racing', drivers: 'Verstappen · Hadjar', points: 522, color: '#3671C6', note: 'Verstappen keeps Red Bull in the fight. Rookie Hadjar shows flashes of brilliance alongside the champion.' },
  { rank: 4, name: 'Mercedes-AMG Petronas', drivers: 'Russell · Antonelli', points: 525, color: '#27f4d2', note: 'A rejuvenated lineup. Russell leads, Antonelli impresses as the next big thing.' },
  { rank: 5, name: 'Aston Martin Aramco', drivers: 'Alonso · Stroll', points: 310, color: '#229971', note: 'The Adrian Newey effect starts to show. Alonso\'s experience extracts the maximum from the car.' },
  { rank: 6, name: 'BWT Alpine F1 Team', drivers: 'Gasly · Colapinto', points: 170, color: '#52e252', note: 'A solid midfield step forward with the new Mercedes PU partnership. Colapinto brings energy to the team.' },
  { rank: 7, name: 'Audi F1 Team', drivers: 'Hülkenberg · Bortoleto', points: 113, color: '#b6babd', note: 'Audi\'s first full season as a works team. Growing pains but signs of future potential.' },
  { rank: 8, name: 'Williams Racing', drivers: 'Albon · Sainz', points: 75, color: '#64c4ff', note: 'Strong driver lineup deserves a better car. Steady progress continues.' },
  { rank: 9, name: 'MoneyGram Haas F1', drivers: 'Ocon · Bearman', points: 50, color: '#2293d1', note: 'Bearman is the highlight. A scrappy outfit that punches above its weight.' },
  { rank: 10, name: 'Racing Bulls', drivers: 'Lawson · Lindblad', points: 25, color: '#1e6176', note: 'Lawson leads while rookie Lindblad learns the ropes. Talent is clear in both seats.' },
  { rank: 11, name: 'Cadillac F1 Team', drivers: 'Bottas · Pérez', points: 13, color: '#C0C0C0', note: 'The new 11th team enters F1 with two veterans. A development year focused on building foundations.' },
]

// Race Calendar Data
export const races = [
  { round: 1, flag: '🇦🇺', name: 'Australian Grand Prix', circuit: 'Albert Park, Melbourne', date: 'Mar 6-8', prediction: '🏆 Hamilton wins on Ferrari debut' },
  { round: 2, flag: '🇨🇳', name: 'Chinese Grand Prix', circuit: 'Shanghai International', date: 'Mar 13-15', prediction: '🏆 Norris dominates from pole' },
  { round: 3, flag: '🇯🇵', name: 'Japanese Grand Prix', circuit: 'Suzuka', date: 'Mar 27-29', prediction: '🏆 Verstappen shows Red Bull\'s pace' },
  { round: 4, flag: '🇧🇭', name: 'Bahrain Grand Prix', circuit: 'Sakhir', date: 'Apr 10-12', prediction: '🏆 Leclerc Ferrari 1-2' },
  { round: 5, flag: '🇸🇦', name: 'Saudi Arabian Grand Prix', circuit: 'Jeddah Corniche', date: 'Apr 17-19', prediction: '🏆 Hamilton under the lights' },
  { round: 6, flag: '🇺🇸', name: 'Miami Grand Prix', circuit: 'Miami International', date: 'May 1-3', prediction: '🏆 Norris takes the fight to Ferrari' },
  { round: 7, flag: '🇨🇦', name: 'Canadian Grand Prix', circuit: 'Circuit Gilles-Villeneuve', date: 'May 22-24', prediction: '🏆 Verstappen masters the rain' },
  { round: 8, flag: '🇲🇨', name: 'Monaco Grand Prix', circuit: 'Circuit de Monaco', date: 'Jun 5-7', prediction: '🏆 Leclerc wins at home again' },
  { round: 9, flag: '🇪🇸', name: 'Spanish Grand Prix', circuit: 'Barcelona-Catalunya', date: 'Jun 12-14', prediction: '🏆 Russell\'s Mercedes breakthrough' },
  { round: 10, flag: '🇦🇹', name: 'Austrian Grand Prix', circuit: 'Red Bull Ring', date: 'Jun 26-28', prediction: '🏆 Verstappen dominates at home' },
  { round: 11, flag: '🇬🇧', name: 'British Grand Prix', circuit: 'Silverstone', date: 'Jul 3-5', prediction: '🏆 Hamilton wins for the crowds' },
  { round: 12, flag: '🇧🇪', name: 'Belgian Grand Prix', circuit: 'Spa-Francorchamps', date: 'Jul 17-19', prediction: '🏆 Piastri\'s breakout drive' },
  { round: 13, flag: '🇭🇺', name: 'Hungarian Grand Prix', circuit: 'Hungaroring', date: 'Jul 24-26', prediction: '🏆 Norris dominates tight track' },
  { round: 14, flag: '🇳🇱', name: 'Dutch Grand Prix', circuit: 'Zandvoort', date: 'Aug 21-23', prediction: '🏆 Verstappen\'s final Zandvoort farewell' },
  { round: 15, flag: '🇮🇹', name: 'Italian Grand Prix', circuit: 'Monza', date: 'Sep 4-6', prediction: '🏆 Ferrari Tifosi dream — Hamilton wins' },
  { round: 16, flag: '🇪🇸', name: 'Madrid Grand Prix', circuit: 'Madrid Street Circuit', date: 'Sep 11-13', prediction: '🏆 Leclerc shines at the new venue' },
  { round: 17, flag: '🇦🇿', name: 'Azerbaijan Grand Prix', circuit: 'Baku City Circuit', date: 'Sep 25-27', prediction: '🏆 Chaos race — Antonelli podium!' },
  { round: 18, flag: '🇸🇬', name: 'Singapore Grand Prix', circuit: 'Marina Bay', date: 'Oct 9-11', prediction: '🏆 Leclerc under the lights' },
  { round: 19, flag: '🇺🇸', name: 'United States Grand Prix', circuit: 'COTA, Austin', date: 'Oct 23-25', prediction: '🏆 Hamilton seals the title deal' },
  { round: 20, flag: '🇲🇽', name: 'Mexican Grand Prix', circuit: 'Autodromo Hermanos Rodriguez', date: 'Oct 30 - Nov 1', prediction: '🏆 Verstappen altitude advantage' },
  { round: 21, flag: '🇧🇷', name: 'Brazilian Grand Prix', circuit: 'Interlagos, São Paulo', date: 'Nov 6-8', prediction: '🏆 Classic Interlagos rain drama' },
  { round: 22, flag: '🇺🇸', name: 'Las Vegas Grand Prix', circuit: 'Las Vegas Strip', date: 'Nov 19-21', prediction: '🏆 Norris shines under neon' },
  { round: 23, flag: '🇶🇦', name: 'Qatar Grand Prix', circuit: 'Lusail International', date: 'Nov 27-29', prediction: '🏆 Hamilton extends the lead' },
  { round: 24, flag: '🇦🇪', name: 'Abu Dhabi Grand Prix', circuit: 'Yas Marina', date: 'Dec 4-6', prediction: '🏆 CHAMPION CROWNED — Hamilton 8x WDC' },
]

// Regulation Changes Data
export const regulations = [
  { icon: '⚡', title: 'New Power Units', description: '50/50 split between Internal Combustion Engine and Electric power. The electric motor now produces ~350kW, making these the most electrified F1 cars ever. MGU-H is gone — replaced by a more powerful MGU-K.', tag: 'POWERTRAIN' },
  { icon: '🦅', title: 'Active Aerodynamics', description: 'Movable front and rear wing elements that adjust in real-time. Cars switch between high-downforce mode for corners and low-drag mode on straights — creating massive speed deltas and dramatic overtaking.', tag: 'AERO' },
  { icon: '⚖️', title: 'Lighter & Smaller Cars', description: 'Minimum weight drops by 30kg to ~768kg. Cars are physically smaller — shorter wheelbase and narrower. This means more agile, more responsive machines that look like they belong on an F1 circuit.', tag: 'CHASSIS' },
  { icon: '🛞', title: 'New Tire Rules', description: 'Lower-profile tires with reduced blanket temperatures. Pirelli\'s new compounds designed specifically for the active aero era — more durable, more consistent, and better for racing wheel-to-wheel.', tag: 'TIRES' },
  { icon: '💰', title: 'Revised Cost Cap', description: 'The budget cap is adjusted for the new era with allowances for PU development. Teams have more freedom in how they allocate resources, but the overall spending is still tightly controlled.', tag: 'FINANCIAL' },
  { icon: '🌍', title: 'Sustainability Focus', description: '100% sustainable fuel mandate. All PU manufacturers must use fully sustainable fuels. F1 aims to be net-zero carbon by 2030, and 2026 is the biggest step toward that goal.', tag: 'SUSTAINABILITY' },
]

// Hot Takes Data
export const hotTakes = [
  { heat: 5, label: 'NUCLEAR', peppers: '🌶️🌶️🌶️🌶️🌶️', title: 'Hamilton wins the title in his first year at Ferrari', description: 'At 41, Lewis Hamilton proves everyone wrong and delivers Ferrari their first Drivers\' Championship since Kimi in 2007. The 8th title cements his GOAT status beyond all doubt.' },
  { heat: 4, label: 'SCORCHING', peppers: '🌶️🌶️🌶️🌶️', title: 'Antonelli finishes ahead of Russell by mid-season', description: 'The Italian wonderkid adapts faster than anyone expected. By the European rounds, he\'s consistently matching and beating George Russell. The future of Mercedes is clear.' },
  { heat: 4, label: 'SCORCHING', peppers: '🌶️🌶️🌶️🌶️', title: 'Cadillac outscore Racing Bulls in their debut season', description: 'The new 11th team, with veterans Bottas and Pérez at the wheel, surprises the paddock by finishing ahead of at least one established team. Experience counts.' },
  { heat: 3, label: 'HOT', peppers: '🌶️🌶️🌶️', title: 'Aston Martin become genuine race winners', description: 'The Newey effect combined with Alonso\'s mastery means Aston Martin win at least 3 races. The green cars are the biggest movers in the new regulation era.' },
  { heat: 3, label: 'HOT', peppers: '🌶️🌶️🌶️', title: 'Active aero creates the best racing we\'ve ever seen', description: 'The DRS-on-steroids effect of active aero means we see 50% more overtakes compared to 2025. Every race has at least one lead change. Fans are absolutely buzzing.' },
  { heat: 5, label: 'NUCLEAR', peppers: '🌶️🌶️🌶️🌶️🌶️', title: 'A rookie scores a podium in the first 5 races', description: 'Whether it\'s Antonelli, Colapinto, Bortoleto, Lindblad, or Hadjar — the chaos of new regs creates openings. One of them seizes their moment spectacularly.' },
]
