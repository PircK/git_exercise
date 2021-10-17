import tkinter
import math
import logging
import os

import logika_igre
import clovek
import racunalnik
import alfabeta

###########################################################################
#               KONSTANTE                                                 #
###########################################################################

STRANICA_SESTKOTNIKA = 20
# visina trikotnikov v sestkotniku
VISINA_TRIKOTNIKA = 3 ** (0.5) * (0.5) * STRANICA_SESTKOTNIKA

PRAZNO = logika_igre.PRAZNO

NI_KONEC = logika_igre.NI_KONEC
NEODLOCENO = logika_igre.NEODLOCENO

# možne barvne kombinacije igralnih polj
# v primeru dodajanja novih je potrebno dopolniti še funkcijo izpis_igralca
# ter izbire v menuju barva_menu
kombinacije_barv = [('red', 'blue'), ('red', 'green'), ('blue', 'green')]


# uporabljeno v Textwidgetu
END = 'end'

###########################################################################
#                               GUI                                       #
###########################################################################

class Gui():

    def __init__(self, master):

        # PLOSCA
        self.plosca = tkinter.Canvas(master)
        self.plosca.grid(row=1, column=0)

        # 'naročimo' se na levi klik miške
        self.plosca.bind("<Button-1>", self.plosca_klik)

        # POLJE ZA SPOROCILA
        self.napis = tkinter.StringVar(master, value='')
        tkinter.Label(master, textvariable=self.napis).grid(row=0, column=0)
        
        # SHRANJEVANJE PODATKOV O POLJIH
        # Ključi so id, vrednosti koordinate.
        self.id_koord = {}
        # Ključi so koordinate (i, j), vrednosti id-ji
        self.koord_id = {}
        
        # ZAČNEMO NOVO IGRO
        self.igra = None
        self.igralec_1 = None # Objekt, ki igra IGRALEC_1 (nastavimo ob začetku igre)
        self.igralec_2 = None # Objekt, ki igra IGRALEC_2 (nastavimo ob začetku igre)

        # najprej nastavimo nastavitve za igro
        # igro zacnemo v barvni kombinaciji rdeca-modra (izbira 0)
        self.barva = tkinter.IntVar(value=0)
        # na polju velikosti 15x15
        self.velikost_matrike = tkinter.IntVar(value=15)
        # v nacinu clovek-racunalnik (izbira 1)
        self.nacin_igre = tkinter.IntVar(value=1)
        # zacnemo igro
        self.zacni_igro()
        
        # ZAPIRANJE OKNA
        # Če uporabnik zapre okno naj se poklice self.zapri_okno
        master.protocol("WM_DELETE_WINDOW", lambda: self.zapri_okno(master))

        # GLAVNI MENU
        glavni_menu = tkinter.Menu(master)
        master.config(menu=glavni_menu)

        # PODMENUJI
        igra_menu = tkinter.Menu(glavni_menu, tearoff=0)
        glavni_menu.add_cascade(label="Igra", menu=igra_menu)

        nacini_menu = tkinter.Menu(glavni_menu, tearoff=0)
        glavni_menu.add_cascade(label="Nastavitve igre", menu=nacini_menu)

        velikost_menu = tkinter.Menu(glavni_menu, tearoff=0)
        glavni_menu.add_cascade(label="Velikost polja", menu=velikost_menu)
        
        barva_menu = tkinter.Menu(glavni_menu, tearoff=0)
        glavni_menu.add_cascade(label="Barva", menu=barva_menu)

        pomoc_menu = tkinter.Menu(glavni_menu, tearoff=0)
        glavni_menu.add_cascade(label="Pomoč", menu=pomoc_menu)


        # IZBIRE V PODMENUJIH        
        igra_menu.add_command(label="Nova igra", command=lambda: self.zacni_igro())

        nacini_menu.add_radiobutton(label="Človek - Človek", variable=self.nacin_igre, value=0, command=lambda: self.zacni_igro())
        nacini_menu.add_radiobutton(label="Človek - Računalnik", variable=self.nacin_igre, value=1, command=lambda: self.zacni_igro())
        nacini_menu.add_radiobutton(label="Računalnik - Človek", variable=self.nacin_igre, value=2, command=lambda: self.zacni_igro())
        nacini_menu.add_radiobutton(label="Računalnik - Računalnik", variable=self.nacin_igre, value=3, command=lambda: self.zacni_igro())
        
        velikost_menu.add_radiobutton(label="10x10", variable=self.velikost_matrike, value=10, command=lambda: self.zacni_igro())
        velikost_menu.add_radiobutton(label="15x15", variable=self.velikost_matrike, value=15, command=lambda: self.zacni_igro())
        velikost_menu.add_radiobutton(label="20x20", variable=self.velikost_matrike, value=20, command=lambda: self.zacni_igro())

        barva_menu.add_radiobutton(label="rdeča-modra", variable=self.barva, value=0, command=lambda: self.zacni_igro())
        barva_menu.add_radiobutton(label="rdeča-zelena", variable=self.barva, value=1, command=lambda: self.zacni_igro())
        barva_menu.add_radiobutton(label="modra-zelena", variable=self.barva, value=2, command=lambda: self.zacni_igro())
       
        pomoc_menu.add_command(label="Navodila", command=lambda: self.odpri_navodila())
    
    ##################################
    #             IGRA               #
    ##################################
    
    def zacni_igro(self):
        '''Nastavi stanje igre na zacetek igre'''
        # Ustavimo vsa vlakna, ki trenutno razmišljajo in pocistimo plosco
        self.prekini_igralce()
        self.plosca.delete('all')
        
        # nastavimo barvo
        self.nastavi_barvo_igralnih_polj()
        # nastavimo velikost
        self.nastavi_velikost_igralnega_polja()
        # shranimo igralce
        self.nastavi_nacin_igre()

        # ustvarimo novo igro
        self.igra = logika_igre.Igra()

        # nastavimo stvari vidne uporabniku
        self.napis.set('Na potezi je {0}.'.format(self.izpis_igralca(logika_igre.drugi)))
        self.napolni_igralno_polje()
        
        # prvi na potezi je igralec 2, saj je prvo polje že pobarvano
        # z barvo igralca 1
        self.igra.na_potezi = logika_igre.drugi
        self.igralec_2.igraj()      

    def prekini_igralce(self):
        """Sporoči igralcem, da morajo nehati razmišljati."""
        if self.igralec_1: self.igralec_1.prekini()
        if self.igralec_2: self.igralec_2.prekini()

    def povleci_potezo(self, i, j):
        '''logiki igre naroci naj povlece potezo, 
        potem pa se ona ukvarja z veljavnostjo''' 
        barva = self.igra.na_potezi
        
        # izvedemo potezo v logiki igre
        poteza = self.igra.izvedi_potezo(i, j)

        # poteza ni bila veljavna, ne naredimo nič
        if poteza == None:
            pass
        # poteza je bila veljavna
        else:
            # pobarvamo polje
            id = self.koord_id[(i, j)]
            self.plosca.itemconfig(id, fill=barva)

            # nadaljujemo igro
            (zmagovalec, zmagovalna_polja) = poteza
            if zmagovalec == NI_KONEC:
                # poklicemo naslednjega igralca
                if self.igra.na_potezi == logika_igre.prvi:
                    self.igralec_1.igraj()
                    self.napis.set('Na potezi je {0}.'.format(self.izpis_igralca(logika_igre.prvi)))
                else:
                    self.igralec_2.igraj()
                    self.napis.set('Na potezi je {0}.'.format(self.izpis_igralca(logika_igre.drugi)))

            else:
                self.konec_igre(zmagovalec, zmagovalna_polja)
                self.prekini_igralce()
                self.igra.na_potezi = None            

    ###########################################
    #          NASTAVITVE IGRE                #
    ###########################################        

    def nastavi_velikost_igralnega_polja(self):
        '''nastavi velikost igralnega polja'''
        velikost_matrike = self.velikost_matrike.get()
        # nastavimo velikost v logiki_igre
        logika_igre.velikost_matrike = velikost_matrike
        # izracunamo sirino in visino
        sirina = VISINA_TRIKOTNIKA * 2 * velikost_matrike + STRANICA_SESTKOTNIKA + 1
        visina = 1.5 * STRANICA_SESTKOTNIKA * velikost_matrike + 0.5 * STRANICA_SESTKOTNIKA + 1
        self.plosca.config(width=sirina, height=visina)
        
    def nastavi_barvo_igralnih_polj(self):
        '''nastavi barvo igralnih polj'''
        kombinacija = self.barva.get()
        logika_igre.prvi = kombinacije_barv[kombinacija][0]
        logika_igre.drugi = kombinacije_barv[kombinacija][1]

    def nastavi_nacin_igre(self):
        '''nastavi igralce'''
        nacini_igre = [(clovek.Clovek(self), clovek.Clovek(self)),
                (clovek.Clovek(self), racunalnik.Racunalnik(self, alfabeta.Alfabeta(alfabeta.globina))),
                (racunalnik.Racunalnik(self, alfabeta.Alfabeta(alfabeta.globina)), clovek.Clovek(self)),
                (racunalnik.Racunalnik(self, alfabeta.Alfabeta(alfabeta.globina)), racunalnik.Racunalnik(self, alfabeta.Alfabeta(alfabeta.globina)))]
        nacin = self.nacin_igre.get()      
        self.igralec_1 = nacini_igre[nacin][0]
        self.igralec_2 = nacini_igre[nacin][1]
        

    ###########################################
    #          OSTALE FUNKCIJE                #
    ###########################################

    def plosca_klik(self, event):
        '''določi koordinate klika in pokliče ustreznega igralca'''
        m = event.x
        n = event.y
        id = self.plosca.find_closest(m, n)[0]
        (i, j) = self.id_koord[id]
        if self.igra.na_potezi == logika_igre.prvi:
            self.igralec_1.klik(i, j)
        elif self.igra.na_potezi == logika_igre.drugi:
            self.igralec_2.klik(i, j)
        else:
            pass

    def narisi_sestkotnik(self, x, y):
        '''nariše šestkotnik in vrne njegov id'''
        a = STRANICA_SESTKOTNIKA
        v = VISINA_TRIKOTNIKA
        t = [x, y + a * 0.5,
             x + v, y,
             x + 2 * v,y + (0.5) * a,
             x + 2 * v, y + 1.5 * a,
             x + v, y + 2 * a,
             x, y + 1.5 * a]
        id = self.plosca.create_polygon(*t, fill=PRAZNO, outline='black')
        return id

    def napolni_igralno_polje(self):
        '''nariše igralno polje sestavljeno iz šestkotnikov'''
        a = STRANICA_SESTKOTNIKA
        v = VISINA_TRIKOTNIKA
        velikost_matrike = logika_igre.velikost_matrike
        for i in range(velikost_matrike): # vrstica
            # preverimo sodost/lihost in tako določimo zamik prvega šestkotnika
            if i % 2 == 0: # lihe vrstice (ker začnemo šteti z 0)
                zacetni_x = 2
                for j in range(velikost_matrike): # stolpec
                    x = zacetni_x + j * 2 * v
                    y = i * 1.5 * a + 2
                    id = self.narisi_sestkotnik(x, y)
                    self.id_koord[id] = (i, j)
                    self.koord_id[(i,j)] = id
            else: # sode vrstice
                zacetni_x = v + 2
                for j in range(velikost_matrike): # stolpec
                    x = zacetni_x + j * 2 * v
                    y = i * 1.5 * a + 2
                    id = self.narisi_sestkotnik(x, y)
                    self.id_koord[id] = (i, j)
                    self.koord_id[(i, j)] = id
        # pobarvamo prvo polje
        self.pobarvaj_prvo_polje()

    def pobarvaj_prvo_polje(self):
        '''pobarva prvo polje z barvo igralca 1 in spremembo zabeleži v logiko igre'''
        i = logika_igre.velikost_matrike // 2
        j = i
        barva = logika_igre.prvi
        sredina = self.koord_id[(i,j)]
        self.plosca.itemconfig(sredina, fill=barva)
        self.igra.zabelezi_spremembo_barve(i, j, barva)
        self.igra.zadnja_poteza = (i, j)
        self.igra.stevilo_pobarvanih_polj += 1

    def izpis_igralca(self, igralec):
        '''pravilno sklanja ime igralca, za izpis uporabniku'''
        if igralec == 'red':
            return 'rdeči'
        elif igralec == 'blue':
            return 'modri'
        elif igralec == 'green':
            return 'zeleni'

    def konec_igre(self, zmagovalec, zmagovalna_polja):
        '''uvede ustrezne spremembe v oknu'''
        # igre je konec, imamo zmagovalca
        if zmagovalec in [logika_igre.prvi, logika_igre.drugi]:
            self.napis.set('Zmagal je {0}.'.format(self.izpis_igralca(zmagovalec)))
            for (i, j) in zmagovalna_polja:
                # odebelimo zmagovalna polja
                id = self.koord_id[(i, j)]
                self.plosca.itemconfig(id, width=3)

        # igre je konec, rezultat je izenacen
        else:
            self.napis.set('Igra je neodločena.')
            
    def zapri_okno(self, master):
        '''Ta metoda se pokliče, ko uporabnik zapre aplikacijo.'''
        self.prekini_igralce()
        # Dejansko zapremo okno.
        master.destroy()
        
    ###########################################
    #          POMOČ UPORABNIKU               #
    ###########################################   

    def odpri_navodila(self):
        '''odpre okno z navodili za igro'''
        pomoc_igra = tkinter.Toplevel()
        pomoc_igra.title("Pravila in navodila")
        pomoc_igra.resizable(width=False, height=False)
        
        navodila1 = tkinter.Text(pomoc_igra, width=65, height=3)
        navodila1.grid(row=0, column=0)
        navodila1.insert(END, 'Pozdravljeni! \n \n')
        navodila1.insert(END, 'V igri SIX morate za zmago tvoriti enega od naslednjih vzorcev:')
        navodila1.config(state='disabled')
        
        vzorci = tkinter.PhotoImage(file=os.path.join('navodila','vzorci.gif'))
        slika1 = tkinter.Label(pomoc_igra, image = vzorci)
        slika1.image = vzorci
        slika1.grid(row=1, column=0)

        navodila2 = tkinter.Text(pomoc_igra, width=65, height=6)
        navodila2.grid(row=2, column=0)
        navodila2.insert(END, '')
        navodila2.insert(END, 'Polje, ki ga želite izbrati, mora imeti vsaj enega že pobarvanega'
                              'soseda, sicer poteza ni veljavna. \n')
        navodila2.insert(END, 'Nad igralnim poljem se nahaja vrstica stanja, kjer vidite \n' 'trenutno stanje igre. \n')
        navodila2.insert(END, 'V primeru zmage se v vrstici stanja izpiše zmagovalec, \n' 'zmagovalni vzorec pa se poudari.')
        navodila2.config(state='disabled')
           
            


if __name__.endswith('__main__'):
    root = tkinter.Tk()
    root.title("SIX")
    root.resizable(width=False, height=False)
    #logging.basicConfig(level=logging.DEBUG)
    aplikacija = Gui(root)
    root.iconbitmap('matica.ico')
    root.mainloop()
