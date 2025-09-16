import express from "express";
import { calculate, Pokemon, Move, Generations } from "@smogon/calc";

const app = express();
app.use(express.json());

app.post("/calc", (req, res) => {
  try {
    const { genReq, attacker, defender, move } = req.body;
    const gen = Generations.get(genReq)
    const result = calculate(
      gen,
      new Pokemon(gen, attacker.species, {
        level: attacker.level,
        ability: attacker.ability,
        item: attacker.item,
        nature: 'Hardy', // Naturaleza neutra
        // por defecto, ivs al máximo
        // sin evs
      }),
      new Pokemon(gen, defender.species, {
        level: defender.level,
        ability: defender.ability,
        item: defender.item,
        nature: 'Hardy', // Naturaleza neutra
      }),
      new Move(gen, move)

    );
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log("API de damage calculator en http://localhost:3000");
});