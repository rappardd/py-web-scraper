import { HiAnime } from "aniwatch";

const hianime = new HiAnime.Scraper();


hianime
  .getEpisodes("berserk-1997-103")
  .then((data) => console.log(data))
  .catch((err) => console.error(err));

// hianime
//   .getEpisodeServers("berserk-1997-103?ep=3123")
//   .then((data) => console.log(data))
//   .catch((err) => console.error(err));

// hianime
//   .getEpisodeSources("berserk-1997-103?ep=3124", "hd-1", "sub")
//   .then((data) => console.log(JSON.stringify(data, null, 2)))
//   .catch((err) => console.error(JSON.stringify(err, null, 2)));

