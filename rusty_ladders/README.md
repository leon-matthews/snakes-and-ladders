
# Rusty Ladders


## Benchmarking

### Crate 'rand'
Initial measurement for 1,000,000 games                     284.1 ms ±   7.7 ms
Pass RNG as parameter                                       213.6 ms ±   4.8 ms
Swap `gen_range()` for `next_u32()`                         175.6 ms ±   2.5 ms

### Crate 'fandrand'
Switch to fastrand::u8()                                    154.7 ms ±   3.6 ms
Put match cases into numerical order                        156.9 ms ±   3.9 ms
