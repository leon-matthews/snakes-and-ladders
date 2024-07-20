
# Rusty Ladders


## Benchmarking

TODO: Profile to see how much time is spent just rolling dice. Right now it
seems like a big proportion. Would the engineering work of breaking that
64-bit random number into 16 4-bit dice rolls, maybe as as custom iterator
into a circulal buffer be worth it? I mean, no, it wouldn't. But it might
be fun!

Something like:

    value: u64 = random()
    lsbyte: u8 = (value & 0xff) as u8;
    value = value >> 8;

### Crate 'rand'
Initial measurement for 1,000,000 games                     284.1 ms ±   7.7 ms
Pass RNG as parameter                                       213.6 ms ±   4.8 ms
Swap `gen_range()` for `next_u32()`                         175.6 ms ±   2.5 ms
Swap `next_u32` for `next_u64()`                            171.8 ms ±   4.3 ms
Enable `lto = "fat"`                                        167.8 ms ±   4.5 ms

### Crate 'fandrand'
Switch to fastrand::u8()                                    154.7 ms ±   3.6 ms
Put match cases into numerical order                        156.9 ms ±   3.9 ms


## Profiling

### Use 'flamegraph' to run benchmark and generate basic flamegraph.

    $ cargo install flamegraph
    $ cargo flamegraph --root

### Use 'hotspot' GUI to explore profile data in-depth

    $ sudo apt install hotspot
    $ sudo chown leon:leon perf.data
    $ hotspot perf.data

### Linux permissions

On Linux the `perf` subsystem requiresc special privileges.

    $ sudo sysctl kernel.perf_event_paranoid=-1
