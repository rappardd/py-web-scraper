import { HiAnime } from "aniwatch";

const hianime = new HiAnime.Scraper();

// const slug = process.argv[2];
// const episode = process.argv[3];
const episode = process.argv[2]
const quality = process.argv[3];
const subtitle = process.argv[4];

// print the arguments
console.error("Arguments:", episode, quality, subtitle);

hianime
  .getEpisodeSources(`${episode}`, quality, subtitle)
  .then((data) => console.log(JSON.stringify(data, null, 2)))
  .catch((err) => console.error(JSON.stringify(err, null, 2)));