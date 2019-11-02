////////////////////////////////////////////////////////////////////////
// Formation of constellations using four-dimensional manhattan distance
////////////////////////////////////////////////////////////////////////

#include <bits/stdc++.h>
using namespace std;

#define nl '\n'

////////////////////////////////////////////////////////////////////////
// Four-dimensional point class, with connections for constellations
//
// 1) A constellation is a group of FOURDs where each FOURD has a
//    manhattan distance of three or less with at least one other
//    FOURD in the constellation
//
// 2) sort_index:  arbitrary per-FOURD-unique value with which to
//                 compare FOURDs
//
// 3) Invariant:  the pOriginator will point to the FOURD with the
//                smallest sort_index in a constellation of FOURDs
//
// 4.1) Invariant:  pOriginator->pOriginator == pOriginator i.e the
//                  constellation originator's pOriginator will point
//                  to itself
//
// 5) Invariant:  *(pOriginator->psetp) will be the set of all pFOURDs
//                in that originator's constellation;
//
// 6)             All non-originator FOURDs will have psetp == NULL

class FOURD {
public:
  static const int MMHD = 3;  // Maximum manhattan distance for forming
                              // a constellation; item (1) above

  int fours[4];        // The four coordinates
  bool failed;         // Flag to note that fscanf failed
  set<FOURD*>* psetp;  // If not null, set of FOURDs in constellation
  FOURD* pOriginator;  // Originator of constellation
  int sort_index;      // An ordering index

  FOURD(int N, FILE* fin=stdin);

  ~FOURD() { if (psetp) delete psetp; }

  // Manhattan distance between two FOURD objects

  int operator-(FOURD& that) {
    int rtn = 0;
    for (int i=0; rtn<=MMHD && i<4; ++i) {
      rtn += abs(fours[i] - that.fours[i]);
    }
    return rtn;
  }
  bool merge(FOURD* that);
};

typedef FOURD *pFOURD, **ppFOURD;
typedef set<FOURD*> SF, *pSF, **ppSF;
typedef SF::iterator SFIT;


////////////////////////////////////////////////////////////////////////
// Merge FOURD constellations if manhattan distance is <= MMHD

bool FOURD::merge(FOURD* that) {

  // Do not test two FOURDs already in the same constellation
  // Do n0t merge two FOURDs that are farther than MMH apart

  if (this->pOriginator == that->pOriginator) return false;
  if ( (*this - *that) > MMHD ) return false;

  // To here, this and that are in different constellations and are also
  // within Manhattan distance FOURD.MMHD of each other

  // Find new originator and mergee; Invariant (3) above

  pFOURD pNew_originator;
  pFOURD pMergee;

  if (this->pOriginator->sort_index < this->pOriginator->sort_index) {
    pNew_originator = this->pOriginator;
    pMergee = that->pOriginator;
  } else {
    pNew_originator = that->pOriginator;
    pMergee = this->pOriginator;
  }

  // Set ->pOriginator in all mergee's psetp elements

  for (SFIT sfit = pMergee->psetp->begin()
      ; sfit != pMergee->psetp->end()
      ; ++sfit
      ) { (*sfit)->pOriginator = pNew_originator; }

  // Copy mergee's set elements to new originator
  // - Invariant 5 above

  pNew_originator->psetp->insert(pMergee->psetp->begin()
                                , pMergee->psetp->end()
                                );

  // Delete mergee set memory allocation and reset pointer to same
  // - Invariant 6 above

  delete pMergee->psetp;
  pMergee->psetp = 0;

  return true;
}

////////////////////////////////////////////////////////////////////////
// FOURD Constructor

FOURD::FOURD(int si_, FILE* fin) {
char c;

  // Read four coordinate values, separated by commas, no spaces before commas

  failed = 7 > fscanf(fin, "%d%c%d%c%d%c%d%c", fours+0, &c, fours+1, &c, fours+2, &c, fours+3, &c);

  if (!failed) {          // If successful:

    psetp = new SF();     // - Set of pFOURDs
    psetp->insert(this);  // - Insert this i.e. 1-point constellation
                          //   - Invariant (5)
    pOriginator = this;   // - This is originator of said constellation
                          //   - Invariant (4)
    sort_index = si_;     // - Use supplied sort index
  } else {
    psetp = 0;            // - If input failed, ensure pointer is nul so des
  }
}


////////////////////////////////////////////////////////////////////////
// [ostream operator<<] overides, for debugging

ostream& operator<<(ostream& out, FOURD& fourd) {
  for (int i=0; i<4; ++i) {
    out << (i ? "," : "") << fourd.fours[i];
  }
  return out;
}

ostream& operator<<(ostream& out, pFOURD pfourd) {
  for (int i=0; i<4; ++i) {
    out << (i ? ',' : '[') << pfourd->fours[i];
  }
  out << ']' ;
  return out;
}


////////////////////////////////////////////////////////////////////////
// The main program

int main(int argc, char** argv) {

  // Allocate 1500 pointers for FOURDs
  ppFOURD ppfourd = new pFOURD[1500];

  int N;

  for (N = 0; N<1500; ++N) {

    // Scan one line from stdin, allocate and populate FOURD
    // - N is used for sort_index; Item (2) above

    ppfourd[N] = new FOURD(N);

    if (ppfourd[N]->failed) {

      // Clean up on failure and exit loop
      // - Assume failure was caused by end of input file

      delete ppfourd[N];
      break;
    }
  }

  ppFOURD ppfourdend = ppfourd + N;  // End of array of pFOURDs

  // Each FOURD is its own constellation
  // Invariant 7) Nconstellations will keep track of number of
  //              constellations

  int Nconstellations = N;

  for (ppFOURD ppouter = ppfourd; ppouter < ppfourdend; ++ppouter) {
     for (ppFOURD ppinner = ppouter; ++ppinner < ppfourdend; ) {
       if ((*ppouter)->merge(*ppinner)) --Nconstellations;
     }
    ;
  }

  cout << N << " points comprise "
       << Nconstellations << " constellations"
       << nl;

  return 0;
}
