# Internationale (B♭ major) - tempo ♩ = 72
BPM = 144
QUARTER = int(60000 / BPM)  # ms per quarter note
HALF = QUARTER * 2
WHOLE = QUARTER * 4
EIGHTH = QUARTER // 2
DOTTED_QUARTER = QUARTER + EIGHTH

# Numbered notation → note names (B♭ major, sharps only)
note_map = {
    0:'REST', 1: 'C', 2: 'D', 3: 'E', 4: 'F', 5: 'G', 6: 'A', 7: 'B'
}


# Function to get note with octave
def get_note(num, octave_shift=0):
    base_octave = 4 + octave_shift
    return f"{note_map[num]}{base_octave}"


# Full song
the_internationale = [
    # Pickup
    (get_note(5), QUARTER), (get_note(1, 1), DOTTED_QUARTER),
    (get_note(7), EIGHTH), (get_note(2,1), EIGHTH),
    (get_note(1,1), EIGHTH), (get_note(5), EIGHTH),
    (get_note(3), EIGHTH), (get_note(6), DOTTED_QUARTER),
    (get_note(6), EIGHTH), (get_note(4), QUARTER),
    (get_note(0), EIGHTH), (get_note(6), EIGHTH),

    (get_note(2,1), DOTTED_QUARTER), (get_note(1,1), EIGHTH),
    (get_note(7), EIGHTH), (get_note(6), EIGHTH),
    (get_note(5), EIGHTH), (get_note(4), EIGHTH),

    # Verse 1
    (get_note(3), HALF+QUARTER), (get_note(5), QUARTER),
    (get_note(1, 1), DOTTED_QUARTER),
    (get_note(7), EIGHTH), (get_note(2,1), EIGHTH),
    (get_note(1,1), EIGHTH), (get_note(5), EIGHTH),
    (get_note(3), EIGHTH), (get_note(6), HALF),
     (get_note(4), EIGHTH),
    (get_note(6), EIGHTH), (get_note(2,1), EIGHTH),
    (get_note(1, 1), EIGHTH), (get_note(7), QUARTER),
    (get_note(2,1),QUARTER), (get_note(4,1),QUARTER),
    (get_note(7), QUARTER), (get_note(1,1), HALF),
    (get_note(1,1), EIGHTH), (get_note(0), EIGHTH),
    (get_note(3,1), EIGHTH), (get_note(2,1), EIGHTH),

    (get_note(7), HALF), (get_note(6), EIGHTH),
    (get_note(7), EIGHTH), (get_note(1,1), EIGHTH),
    (get_note(6), EIGHTH), (get_note(7), HALF),
    (get_note(5), EIGHTH), (get_note(5), EIGHTH),
    (get_note(4), EIGHTH), (get_note(5), EIGHTH),

    (get_note(6), DOTTED_QUARTER), (get_note(6), EIGHTH),
    (get_note(2,1), DOTTED_QUARTER), (get_note(1,1), EIGHTH),
    (get_note(7), HALF), (get_note(7), EIGHTH),
    (get_note(0), EIGHTH), (get_note(2,1), QUARTER),
    (get_note(2,1), DOTTED_QUARTER), (get_note(7), EIGHTH),
    (get_note(5), EIGHTH), (get_note(5), EIGHTH),
    (get_note(4), EIGHTH), (get_note(5), EIGHTH),
    (get_note(3,1), HALF), (get_note(1,1), EIGHTH),

    (get_note(6), EIGHTH), (get_note(7), EIGHTH),
    (get_note(1,1), EIGHTH), (get_note(7), QUARTER),
    (get_note(2,1), QUARTER), (get_note(1,1), int(EIGHTH+EIGHTH/2)),
    (get_note(1,1), int(EIGHTH/2)), (get_note(6), QUARTER),
    (get_note(5), HALF), (get_note(5), EIGHTH),
    (get_note(0), EIGHTH),

    # (get_note(3,1), int(EIGHTH+EIGHTH/2)),
    # (get_note(2,1), int(EIGHTH/2)), (get_note(1,1), HALF),
    # (get_note(5), DOTTED_QUARTER), (get_note(3), EIGHTH),
    # (get_note(6), HALF), (get_note(4), QUARTER),
    # (get_note(2,1), int(EIGHTH+EIGHTH/2)), (get_note(1,1), int(EIGHTH/2)),
    #
    # (get_note(7), HALF), (get_note(6), QUARTER),
    # (get_note(5), QUARTER), (get_note(5), HALF),
    # (get_note(5), EIGHTH), (get_note(0), EIGHTH),
    # (get_note(5), QUARTER), (get_note(3,1), HALF),
    # (get_note(2,1), QUARTER), (get_note(5), QUARTER),
    # (get_note(1,1), HALF), (get_note(7), DOTTED_QUARTER),
    # (get_note(7), EIGHTH), (get_note(6), DOTTED_QUARTER),
    # (get_note(5), EIGHTH), (get_note(6), QUARTER),
    # (get_note(2,1), QUARTER),



    # ...
    # (All remaining measures of verses and chorus would follow exactly
    # in the same format — merged ties, correct octaves, durations from tempo)
]