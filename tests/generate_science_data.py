import os
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

def create_file(filename, content):
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        f.write(content)

def generate_noise():
    """Generates filler scientific text to dilute the search pool."""
    jargon = ["nucleotide", "transcription", "helix", "polymerase", "ligase", "in-vitro", "substrate"]
    return " ".join([f"The {random.choice(jargon)} exhibited significant variance in the {random.choice(jargon)} phase." for _ in range(50)])

def generate_dataset():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    print(f"🧬 Generating Scientific Dataset in {DATA_DIR}...")

    # --- THE GOLDEN NEEDLES (Relevant Info) ---
    
    # Document A: The Mechanism of Cas9
    create_file("mechanism_cas9.md", """
    # Molecular Mechanism of CRISPR-Cas9
    The Cas9 nuclease is guided to its DNA target by a single-guide RNA (sgRNA).
    Crucially, Cas9 requires a specific Protospacer Adjacent Motif (PAM) sequence to bind.
    For Streptococcus pyogenes Cas9 (SpCas9), this PAM sequence is **5'-NGG-3'**.
    Upon binding, Cas9 induces a double-strand break (DSB) typically 3 base pairs upstream of the PAM.
    """)

    # Document B: The Mechanism of Cas12a (The Distractor)
    create_file("mechanism_cas12a.md", """
    # Distinct Features of Cas12a (Cpf1)
    Unlike Cas9, the Cas12a nuclease processes its own crRNA and does not require a tracrRNA.
    The PAM sequence requirement for Cas12a is distinct: it recognizes a T-rich PAM, typically **5'-TTTV-3'**.
    Furthermore, Cas12a creates a 'staggered' cut (sticky ends) rather than the blunt ends produced by Cas9.
    """)

    # Document C: Repair Pathways
    create_file("repair_pathways.md", """
    # NHEJ vs HDR Repair Mechanisms
    Following a double-strand break, the cell repairs DNA via:
    1. **Non-Homologous End Joining (NHEJ):** Error-prone, often leading to insertions/deletions (indels) that disrupt gene function.
    2. **Homology-Directed Repair (HDR):** Precise editing requiring a donor template. This pathway is less efficient and strictly regulated by the cell cycle (S/G2 phase).
    """)

    # --- THE HAYSTACK (Irrelevant Noise) ---
    # We create 15 "filler" files to simulate a busy database.
    # This forces the Retriever to actually work hard to find the right 3 docs.
    for i in range(1, 16):
        content = f"# Experimental log {i}\n" + generate_noise()
        create_file(f"log_data_{i}.txt", content)

    print("✅ Created 3 Target files and 15 Noise files.")

if __name__ == "__main__":
    generate_dataset()
