import logging

#######################################################
#                      PARAMETRI                      #
#######################################################

PRAZNO = ''
NEODLOCENO = "neodločeno"
NI_KONEC = "ni konec"

# VELIKOST IGRALNEGA POLJA
# nastavi gui ob začetku igre glede na željeno izbiro
velikost_matrike = None

# barva igralca_1 in igralca_2
# nastavi gui ob začetku igre, glede na izbrano barvno kombinacijo
prvi = None
drugi = None

#######################################################
#                        IGRA                         #
#######################################################

class Igra():

    def __init__(self):

        # SEZNAM ŠESTKOTNIKOV
        self.igralno_polje = [[PRAZNO for j in range(velikost_matrike)] for i in range(velikost_matrike)]

        # prvo polje pobarvamo z barvo prvega igralca, zato je na potezi drugi
        self.na_potezi = drugi

        self.zgodovina = []
        
        # prvo spremembo zadnje poteze in števila pobarvanih polj naredi gui, 
        # ko pobarva sredinsko polje, glede na velikost igralnega polja
        self.zadnja_poteza = None
        self.stevilo_pobarvanih_polj = 0
        
        
    ##############
    # VELJAVNOST #
    ##############
    
    def veljavnost_poteze(self, i, j):
        '''vrne True, če je poteza (i, j) veljavna'''
        if self.na_potezi == None:
            assert False, "gledamo veljavnost poteze, ko nihče ni na potezi"

        if self.igralno_polje[i][j] != PRAZNO:
            return False
        else:
            # gledamo, ali je kak neprazen sosed
            stevilo_sosedov = 0
            for (x,y) in seznam_sosedov(i, j):
                if self.igralno_polje[x][y] != PRAZNO:
                    return True
            # ni bilo nepraznega soseda
            return False
            
    def veljavne_poteze(self):
        '''vrne seznam veljavnih potez'''
        poteze = set()
        for i in range(velikost_matrike):
            for j in range(velikost_matrike):
                if self.igralno_polje[i][j] != PRAZNO:
                    for (x,y) in seznam_sosedov(i,j):
                        if self.igralno_polje[x][y] == PRAZNO:
                            poteze.add((x,y))
        return poteze  

        
    ##################
    #     VZORCI     #
    ##################
    
    # Funkcija za vsak vzorec posebej nam olajša pregledovanje stanja igre,
    # saj ni potrebno za vsako polje pogledati vseh vzorecev
        
    def vodoravna_crta(self, i, j):
        '''vrne vzorec za vodoravno crto, ce je le-ta veljavna sestka'''
        vodoravna_crta = [(i, j), (i, j+1), (i, j+2), (i, j+3), (i, j+4), (i, j+5)]
        
        if veljavna_sestka(vodoravna_crta):
            return vodoravna_crta
        else:
            return []

    def narascajoca_crta(self, i, j):
        '''vrne vzorec za narascajoco crto, ce je le-ta veljavna sestka'''
        if i % 2 == 0: # lihe vrstice
            narascajoca_crta = [(i, j), (i+1, j-1), (i+2, j-1), (i+3, j-2), (i+4, j-2), (i+5, j-3)]
        else:   # sode
            narascajoca_crta = [(i, j), (i+1, j), (i+2, j-1), (i+3, j-1), (i+4, j-2), (i+5, j-2)]
            
        if veljavna_sestka(narascajoca_crta):
            return narascajoca_crta
        else:
            return []
            
    def padajoca_crta(self, i, j):
        '''vrne vzorec za padajoco crto, ce je le-ta veljavna sestka'''
        if i % 2 == 0: # lihe vrstice
            padajoca_crta = [(i, j), (i+1, j), (i+2, j+1), (i+3, j+1), (i+4, j+2), (i+5, j+2)]
        else:  # sode
            padajoca_crta = [(i, j), (i+1, j+1), (i+2, j+1), (i+3, j+2), (i+4, j+2), (i+5, j+3)]
            
        if veljavna_sestka(padajoca_crta):
            return padajoca_crta
        else:
            return []
            
    def trikotnik_na_glavo(self, i, j):
        '''vrne vzorec za trikotnik obrnjen na glavo, ce je le-ta veljavna sestka'''
        if i % 2 == 0: # lihe vrstice
            trikotnik_na_glavo = [(i, j), (i, j+1), (i, j+2), (i+1, j), (i+1, j+1), (i+2, j+1)]
        else:   # sode
            trikotnik_na_glavo = [(i, j), (i, j+1), (i, j+2), (i+1, j+1), (i+1, j+2), (i+2, j+1)]
        
        if veljavna_sestka(trikotnik_na_glavo):
            return trikotnik_na_glavo
        else:
            return []
        
    def trikotnik(self, i, j):
        '''vrne vzorec za trikotnik, ce je le-ta veljavna sestka'''
        if i % 2 == 0: # lihe vrstice
            trikotnik = [(i, j), (i+1, j-1), (i+1, j), (i+2, j-1), (i+2, j), (i+2, j+1)]
        else:   # sode
            trikotnik = [(i, j), (i+1, j), (i+1, j+1), (i+2, j-1), (i+2, j), (i+2, j+1)]
        
        if veljavna_sestka(trikotnik):
            return trikotnik
        else:
            return []
            
    def rozica(self, i, j):
        '''vrne vzorec za rozico, ce je le-ta veljavna sestka'''
        if i % 2 == 0: # lihe vrstice
            rozica = [(i, j), (i, j+1), (i+1, j+1), (i+2, j+1), (i+2, j), (i+1, j-1)]
        else:   # sode
            rozica = [(i, j), (i, j+1), (i+1, j+2), (i+2, j+1), (i+2, j), (i+1, j)]
        
        if veljavna_sestka(rozica):
            return rozica
        else:
            return []
 
    def zmagovalni_vzorci(self, i, j):
        '''vrne slovar vseh moznih zmagovalnih vzorcev za polje (i,j)'''       
        vodoravna_crta = self.vodoravna_crta(i, j)
        narascajoca_crta = self.narascajoca_crta(i, j)
        padajoca_crta = self.padajoca_crta(i, j)
        trikotnik_na_glavo = self.trikotnik_na_glavo(i, j)
        trikotnik = self.trikotnik(i, j)
        rozica = self.rozica(i, j)

        vzorci = {'vodoravna_crta':vodoravna_crta, 'narascajoca_crta':narascajoca_crta,
                  'padajoca_crta':padajoca_crta, 'trikotnik':trikotnik,
                  'trikotnik_na_glavo':trikotnik_na_glavo, 'rozica':rozica}
        return vzorci
        
        
    ##################
    # IZVEDBA POTEZE #
    ##################
    
    def zabelezi_spremembo_barve(self, i, j, barva):
        '''na (i,j) mesto v igralnem polju zapiše barvo'''
        self.igralno_polje[i][j] = barva

    def izvedi_potezo(self, i, j):
        '''če je poteza veljavna jo izvede in vrne (zmagovalec, zmagovalna_polja), sicer vrne None'''
        
        # poteza je veljavna
        if self.veljavnost_poteze(i, j) == True:
            
            # shranimo igralno polje preden izvedemo potezo
            # v primeru shranjevanja novih podatkov, je potrebno popraviti 
            # še funkciji razveljavi in kopija
            kopija_polja = [self.igralno_polje[i][:] for i in range(velikost_matrike)]
            barva = self.na_potezi
            poteza = self.zadnja_poteza
            stevilo_polj = self.stevilo_pobarvanih_polj
            self.zgodovina.append((kopija_polja, barva, poteza, stevilo_polj))

            # zabelezimo spremembo barve
            self.zabelezi_spremembo_barve(i, j, barva)
            
            # zabelezimo potezo kot zadnjo opravljeno
            self.zadnja_poteza = (i, j)
            
            # povečamo število pobarvanih polj
            self.stevilo_pobarvanih_polj += 1

            # preverimo, ali je igre morda ze konec
            (zmagovalec, zmagovalna_polja) = self.stanje_igre()
            if zmagovalec == NI_KONEC:
                # spremenimo igralca na potezi
                self.na_potezi = nasprotnik(barva)
            else:
                # spremenimo igralca na potezi na None
                self.na_potezi = None
            return (zmagovalec, zmagovalna_polja)
        
        # poteza ni veljavna
        else:
            return None


    ###############
    # STANJE IGRE #
    ###############           

    def stanje_igre(self):
        '''Vrne (zmagovalec, zmagovalna_polja), ce je nekdo zmagal, (NEODLOCENO, None) ce je plosca polna
        in ni zmagovalca, sicer vrne (NI_KONEC, None)'''
  
        # pogledamo zadnjo opravljeno potezo in njeno barvo
        (i, j) = self.zadnja_poteza
        barva = self.igralno_polje[i][j]
        
        # Da bi se izognili pregledovanju vseh vzorcev za vsa polja v igralnem polju, 
        # smo definirali funkcijo mozni_zacetki_zmagovalnih_sestic, ki za vsak vzorec 
        # vrne tista polja, s katerimi se izbrani vzorec lahko začne 
        # (in vsebuje (i,j) - pravkar opravljeno potezo) ter tako tvori 
        # zmagovalno šestko. Nato bomo za vsak začetek z ustrezno funkcijo generirali 
        # še preostala polja v vzorcu in preverili koliko jih je ustrezne barve.
        
        # dobimo slovar z možnimi začetnimi polji šestic, za vsak vzorec posebej
        zacetki_vzorcev = mozni_zacetki_zmagovalnih_sestic(i, j)
        
        for vzorec in zacetki_vzorcev:
            # za vsak vzorec bomo pregledali točno določena polja,
            zacetki_vzorca = zacetki_vzorcev[vzorec]
            
            for (x,y) in zacetki_vzorca:
                # preverimo del katerega vzorca je polje, 
                # da lahko pokličemo ustrezno funkcijo
                if vzorec == 'vodoravna_crta':
                    polja = self.vodoravna_crta(x, y)
                elif vzorec == 'narascajoca_crta':
                    polja = self.narascajoca_crta(x, y)
                elif vzorec == 'padajoca_crta':
                    polja = self.padajoca_crta(x, y)
                elif vzorec == 'trikotnik_na_glavo':
                    polja = self.trikotnik_na_glavo(x, y)
                elif vzorec == 'trikotnik':
                    polja = self.trikotnik(x, y)
                elif vzorec == 'rozica':
                    polja = self.rozica(x, y)
                    
                # v primeru, da polja ne tvorijo veljavne šestke, nam funkcije 
                # vrnejo prazen seznam, torej nas zanimajo le neprazni seznami
                if polja != []:
                    stevilo_polj_enake_barve = 0
                    for (z, w) in polja:
                        if self.igralno_polje[z][w] == barva:
                            stevilo_polj_enake_barve += 1
                        else:
                            break
                    # našli smo vzorec sestavljen iz šestih polj
                    # enake barve, torej imamo zmagovalca "barva"
                    if stevilo_polj_enake_barve == 6:
                        return (barva, polja)
                    
        # igralno polje je polno
        if self.stevilo_pobarvanih_polj == velikost_matrike * velikost_matrike:
            return (NEODLOCENO, None)

        # zmagovalca ni in igralno polje ni polno
        return (NI_KONEC, None)
              
         
    ########
    # .... #
    ########

    def razveljavi(self):
        '''razveljavi zadnjo potezo'''
        self.igralno_polje, self.na_potezi, self.zadnja_poteza, self.stevilo_pobarvanih_polj = self.zgodovina.pop()

    def kopija(self):
        '''vrne kopijo igre'''
        k = Igra()
        k.igralno_polje = [self.igralno_polje[i][:] for i in range(velikost_matrike)]
        k.na_potezi = self.na_potezi
        k.zadnja_poteza = self.zadnja_poteza
        k.stevilo_pobarvanih_polj = self.stevilo_pobarvanih_polj
        return k

#######################################################
#                  OSTALE FUNKCIJE                    #
#######################################################

def veljavno_polje(x,y):
    '''Vrne True, če polje obstaja, sicer False'''
    return (0 <= x < velikost_matrike and 0 <= y < velikost_matrike)

def veljavna_sestka(lst):
    '''Vrne True, če so vsa polja v šestki veljavna'''
    for (x,y) in lst:
        if not veljavno_polje(x,y):
            return False
    return True

def seznam_sosedov(i, j):
    '''vrne seznam koordinat veljavnih sosedov'''
    if i % 2 == 0: # lihe (steti zacnemo z 0)
        kandidati = [(i-1, j-1), (i, j-1), (i+1, j-1), (i+1, j), (i, j+1), (i-1, j)]
    else: # sode
        kandidati = [(i-1, j), (i, j-1), (i+1, j), (i+1, j+1), (i, j+1), (i-1, j+1)]
    return [(i,j) for (i,j) in kandidati if veljavno_polje(i,j)]
        
def mozni_zacetki_zmagovalnih_sestic(i, j):
    '''vrne slovar vseh polj, s katerimi bi se lahko začela ena od zmagovalnih 
    šestic ob predpostavki, da smo ravnokar pobarvali (i,j)-to polje '''
    
    if i % 2 == 0: # lihe (štejemo od 0)
        kandidati = {'vodoravna_crta': [(i, j-5), (i, j-4), (i, j-3), (i, j-2), (i, j-1), (i, j)],
                     'padajoca_crta': [(i-5, j-3), (i-4, j-2), (i-3, j-2), (i-2, j-1), (i-1, j-1),(i, j)],
                     'narascajoca_crta': [(i-5, j+2), (i-4, j+2), (i-3, j+1), (i-2, j+1), (i-1, j), (i, j)],
                     'rozica': [(i-2, j-1), (i-2, j), (i-1, j-2), (i-1, j), (i, j-1), (i, j)],
                     'trikotnik_na_glavo': [(i-2, j-1), (i-1, j-2), (i-1, j-1), (i, j-2), (i, j-1), (i, j)],
                     'trikotnik': [(i-2, j-1), (i-2, j), (i-2, j+1), (i-1, j-1), (i-1, j), (i, j)]}
    else:   # sode
        kandidati = {'vodoravna_crta': [(i, j-5), (i, j-4), (i, j-3), (i, j-2), (i, j-1), (i, j)],
                     'padajoca_crta': [(i-5, j-2), (i-4, j-2), (i-3, j-1), (i-2, j-1), (i-1, j), (i, j)],
                     'narascajoca_crta': [(i-5, j+3), (i-4, j+2),(i-3, j+2), (i-2, j+1), (i-1, j+1), (i, j)],
                     'rozica': [(i-2, j-1), (i-2, j), (i-1, j-1), (i-1, j+1), (i, j-1), (i, j)],
                     'trikotnik_na_glavo': [(i-2, j-1), (i-1, j-1), (i-1, j), (i, j-2), (i, j-1), (i, j)],
                     'trikotnik': [(i-2, j-1), (i-2, j), (i-2, j+1), (i-1, j), (i-1, j+1), (i, j)]}
    veljavni_kandidati = {}
    for vzorec in kandidati:
        veljavni_kandidati[str(vzorec)]=[]
        for (x,y) in kandidati[vzorec]:
            if veljavno_polje(x, y):
                veljavni_kandidati[str(vzorec)].append((x, y))
    return veljavni_kandidati
    
def nasprotnik(igralec):
    """Vrne nasprotnika od igralca."""
    if igralec == prvi:
        return drugi
    elif igralec == drugi:
        return prvi
    else:
        assert False, "neveljaven nasprotnik"
