
//~ use fastrand;
use rand::prelude::*;


fn main() {
    let mut num_rolls = 0;

    // Use strong default RNG to seed faster non-cryptographic generator.
    // We can then create multiple small RNGs, one per work-unit.
    let mut thread_rng = rand::thread_rng();
    let mut rng = SmallRng::from_rng(&mut thread_rng).unwrap();

    for _ in 1..=1_000_000 {
        num_rolls = snakes_and_ladders(&mut rng);
    }
    println!("Finished game in {} rolls", num_rolls);
}


fn snakes_and_ladders(rng: &mut SmallRng) -> i32 {
    let mut num_rolls = 0;
    let mut place = 0;

    loop {
        // Roll the dice
        //~ let roll = rng.gen_range(1..=6);            // 227ms for 1e6 games
        let roll = rng.next_u64() % 6 + 1;              // 176ms for 1e6 games
        num_rolls += 1;

        // Where did you end up?
        let landed = place + roll;

        // Where did you *really* end up?
        place = match landed {
            // Ladders
            1 => 38,
            4 => 14,
            9 => 31,
            21 => 42,
            28 => 84,
            36 => 44,
            51 => 67,
            71 => 91,
            80 => 100,

            // Snakes
            98 => 78,
            95 => 75,
            93 => 73,
            87 => 24,
            64 => 60,
            62 => 19,
            56 => 53,
            49 => 11,
            48 => 26,
            16 => 6,

            // Too high? Stay where you are.
            n if n > 100 => place,

            // Normal move
            _ => landed,
        };

        if place == 100 { break; }
    };

    num_rolls
}
