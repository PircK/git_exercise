class Clovek():

    def __init__(self, gui):
        self.gui = gui

    def igraj(self):
        # Smo na potezi. Zaenkrat ne naredimo nič, ampak
        # čakamo, da bo uporanik kliknil na ploščo. Ko se
        # bo to zgodilo, nas bo Gui obvestil preko metode
        # klik.
        pass

    def prekini(self):
        # To metodo kliče GUI, če je treba prekiniti razmišljanje.
        # Človek jo lahko ignorira.
        pass

    def klik(self, i, j):
        '''povlečemo potezo (i, j)'''
        self.gui.povleci_potezo(i, j)