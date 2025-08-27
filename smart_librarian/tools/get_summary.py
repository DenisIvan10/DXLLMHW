# Tool get_summary_by_title()
from typing import Dict

book_summaries_dict: Dict[str, str] = {
    "1984": (
        "Romanul lui George Orwell descrie o societate distopică dominată de Big Brother, "
        "în care supravegherea totală și rescrierea trecutului sunt instrumente de control. "
        "Winston Smith lucrează la Ministerul Adevărului și încearcă să păstreze o fărâmă de "
        "umanitate, iubire și gândire liberă. Povestea explorează propaganda, limbajul ca unealtă "
        "de dominație și fragilitatea adevărului într-un stat totalitar."
    ),
    "The Hobbit": (
        "Bilbo Baggins este smuls din confortul său de acasă pentru a însoți treisprezece pitici "
        "și pe Gandalf într-o călătorie spre Muntele Singuratic. Drumul este presărat cu troli, "
        "goblini, păianjeni uriași și întâlnirea cu Gollum, unde Bilbo găsește Inelul. Bilbo "
        "descoperă curajul, ingeniozitatea și valoarea prieteniei, maturizându-se de la un hobbit "
        "timid la un erou neașteptat."
    ),
    "To Kill a Mockingbird": (
        "Prin ochii lui Scout Finch, romanul prezintă un proces de crimă marcat de rasism în Alabama. "
        "Atticus Finch, tatăl ei, apără un bărbat de culoare acuzat pe nedrept, arătând ce înseamnă "
        "curajul moral într-o comunitate prejudecată. Prietenia, empatia și pierderea inocenței sunt "
        "miezul narațiunii."
    ),
    "Pride and Prejudice": (
        "Elizabeth Bennet se confruntă cu prejudecăți sociale și neînțelegeri alături de enigmaticul "
        "Mr. Darcy. Satira lui Austen surprinde normele de clasă, căsătoria și independența feminină, "
        "conducând la o maturizare afectivă și la o iubire bazată pe respect."
    ),
    "Harry Potter and the Sorcerer's Stone": (
        "Harry află că este vrăjitor și ajunge la Hogwarts, unde leagă prietenii cu Ron și Hermione. "
        "Descoperă misterul Piatrei Filozofale și se confruntă cu primele ecouri ale lui Voldemort. "
        "Cartea pune temelia unei lumi magice despre prietenie, curaj și apartenență."
    ),
    "The Great Gatsby": (
        "În New York-ul anilor ’20, naratorul Nick Carraway îl observă pe Jay Gatsby, obsedat de "
        "iubirea pentru Daisy. Strălucirea petrecerilor ascunde golul moral și iluzia „visului american”. "
        "Romanul radiografiază dorința, bogăția și deziluzia."
    ),
    "Moby Dick": (
        "Căpitanul Ahab pornește într-o vânătoare obsesivă a balenei albe, Moby Dick. "
        "Narațiunea îmbină aventură maritimă, reflecții filosofice și simbolism amplu despre destin, "
        "natura indiferentă și nebunia omului în fața absolutului."
    ),
    "Brave New World": (
        "O societate eugenică și hiper-tehnologică oferă plăcere și stabilitate prin condiționare. "
        "Individul liber devine „anomalie” într-o lume fără suferință, dar și fără profunzime. "
        "Huxley avertizează asupra prețului controlului și al confortului total."
    ),
    "The Catcher in the Rye": (
        "Holden Caulfield, exmatriculat, rătăcește prin New York căutând autenticitate într-o lume "
        "pe care o consideră „falsă”. Monologul său dezvăluie vulnerabilitate, singurătate și dorința "
        "de a proteja inocența copilăriei."
    ),
    "The Lord of the Rings: The Fellowship of the Ring": (
        "Frodo moștenește Inelul Puterii și pornește, alături de Frăție, într-o misiune de a-l distruge. "
        "Drumul trece prin pericole mitice și alegeri morale grele. Prietenia, sacrificiul și speranța "
        "stau împotriva corupției Inelului."
    ),
    "Fahrenheit 451": (
        "Într-un viitor în care cărțile sunt arse, pompierul Guy Montag își descoperă curiozitatea și "
        "sete de cunoaștere. Confruntarea cu cenzura și conformismul îl împinge să caute libertatea "
        "intelectuală și sensul personal."
    ),
    "Crime and Punishment": (
        "Raskolnikov comite o crimă, justificându-și fapta prin teorii despre oameni „extraordinari”. "
        "Romanul urmărește tortura sa psihologică, întâlnirea cu compasiunea Sonei și drumul spre "
        "remușcare și mântuire."
    ),
}

def get_summary_by_title(title: str) -> str:
    """Returnează rezumatul complet pentru titlul exact, sau mesaj util dacă nu există."""
    return book_summaries_dict.get(title, "Nu am găsit un rezumat complet pentru acest titlu.")
