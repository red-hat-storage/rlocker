class CustomList(list):
    def __init__(self, l, no_duplicates=False):
        self.no_duplicates = no_duplicates
        self.l = l
        self.eliminate_duplicates()
        self.elimininate_new_lines()
        super(CustomList, self).__init__(self.l)

    def remove_if_exist(self, v):
        try:
            self.remove(v)
        except ValueError:
            pass

    def elimininate_new_lines(self):
        self.l = [e.replace("\n", "") for e in self.l]

    def eliminate_duplicates(self):
        """
        Eliminate duplicates if asked so
        """
        if self.no_duplicates:
            # Using set to eliminate duplicates
            # The Order of the elements are not important, in this case,
            # It could be sorted anyway, if needed with sort()
            eliminated_set = set(self.l)
            eliminated_list = list(eliminated_set)
            self.l = eliminated_list
