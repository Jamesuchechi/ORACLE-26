export const getFlagUrl = (teamName) => {
  const mapping = {
    'Argentina': 'ar', 'Brazil': 'br', 'Portugal': 'pt', 'France': 'fr',
    'Spain': 'es', 'England': 'gb', 'Germany': 'de', 'Italy': 'it',
    'Belgium': 'be', 'Netherlands': 'nl', 'Croatia': 'hr', 'Uruguay': 'uy',
    'Colombia': 'co', 'Mexico': 'mx', 'USA': 'us', 'Canada': 'ca',
    'Morocco': 'ma', 'Senegal': 'sn', 'Japan': 'jp', 'South Korea': 'kr',
    'Iran': 'ir', 'Australia': 'au', 'Switzerland': 'ch', 'Denmark': 'dk',
    'Scotland': 'gb-sct', 'Poland': 'pl', 'Peru': 'pe', 'Chile': 'cl',
    'Ecuador': 'ec', 'Paraguay': 'py', 'Cameroon': 'cm', 'Nigeria': 'ng',
    'Ghana': 'gh', 'Egypt': 'eg', 'Algeria': 'dz', 'Tunisia': 'tn',
    'Saudi Arabia': 'sa', 'Qatar': 'qa', 'UAE': 'ae', 'Turkey': 'tr',
    'Panama': 'pa', 'Serbia': 'rs', 'Mexico': 'mx', 'Paraguay': 'py',
    'Bosnia': 'ba', 'Cameroon': 'cm'
  };
  const code = mapping[teamName] || 'un';
  return `https://flagcdn.com/w80/${code.toLowerCase()}.png`;
};
