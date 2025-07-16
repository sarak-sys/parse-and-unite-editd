import statistics
import math

class United:
    """
    could not think about somethimg more convinient or smart
    so i created this class for the merger file
    a new data type to unite all seq from all dict_peptides
    count all appearances in all files
    ratios separately
    """
    def __init__(self, seq, prot, count, num_of_files, mode, start, end, heavy, light):
        self.in_file = set()    # if seq in all files then the this field will be {1,2,3,...n}
        self.seq: str = seq
        self.protein: str = prot
        self.protein_count = 0   # number of appearance of prot in all united dict
        self. sum_count: int = count
        self.start = start
        self.end = end
        self.ratio_dict = {}
        self.log_dict = {}
        #these following two dictionaries are added to add view the heavy\light columns in the united file
        self.heavy_dict = {}
        self.light_dict = {}
        self.count_psm_heavy = heavy
        self.count_psm_light = light
        if mode == "default" or mode == "lysine":
            for i in range(num_of_files):
                self.ratio_dict[i] = ""
                self.log_dict[i] = ""
                self.heavy_dict[i]=""
                self.light_dict[i]=""
        elif mode == "label":
            self.count_dict = {}
            for i in range(num_of_files):
                self.count_dict[i] = ""
            self.peak_area_dict = {}
            for i in range(num_of_files):
                self.peak_area_dict[i] = ""
            self.peak_intensity_dict = {}
            for i in range(num_of_files):
                self.peak_intensity_dict[i] = ""
            self.rt_seconds_dict = {}
            for i in range(num_of_files):
                self.rt_seconds_dict[i] = ""
            self.ion_dict = {}
            for i in range(num_of_files):
                self.ion_dict[i] = ""

        self.avg = -1
        self.median = -1
        self.st_deviation = -1
        self.mode = mode

    def add_sum_count(self, count):
        self.sum_count += count

    def add_count_psm_heavy(self, heavy):
        self.count_psm_heavy += heavy

    def add_count_psm_light(self, light):
        self.count_psm_light += light

    def add_ratio(self, i, ratio):
        """
        ratio 0         ->   log -10
        ratio num dev 0 ->   log 10
        ratio 0 dev 0   ->   log empty
        ratio number    -> log base 10 of number
        """
        #print(type(ratio))
        #print(ratio)
        self.ratio_dict[i] = ratio
        if ratio == "" or ratio == "0 dev 0":
            self.log_dict[i] = ""
        elif ratio == 0:
            self.log_dict[i] = -10
        elif ratio == "num dev 0":
            self.log_dict[i] = 10
        else:
            self.log_dict[i] = math.log(ratio, 2)

        self._calc_all()
    
    #Values of the light/heavy columns
    def add_heavy1(self, i, heavy):
        self.heavy_dict[i] = heavy

    def add_light1(self, i, light):
        self.light_dict[i] = light


    def add_all_label_mode(self, i, counter, peak_area, peak_intensity, rt_seconds, ions):
        self.count_dict[i] = counter
        self.peak_area_dict[i] = peak_area
        self.peak_intensity_dict[i] = peak_intensity
        self.rt_seconds_dict[i] = rt_seconds
        self.ion_dict[i] = ions

    def print_united(self):
        print("seq is " +self.seq)
        print("prot is " +self.protein)
        print( "count is " + str(self.sum_count))
        print ("ratio dict is " + str(self.ratio_dict))

    def class_to_list(self, mode):
        pep = []
        pep.append(self.seq)
        pep.append(self.protein)
        pep.append(self.sum_count)
        pep.append(self.start)
        pep.append(self.end)
        if mode == "default" or mode == "lysine":
            for i in range(len(self.ratio_dict)):
                pep.append(self.ratio_dict[i])
                pep.append(self.log_dict[i])
                pep.append(self.heavy_dict[i])
                pep.append(self.light_dict[i])
            pep.append(self.avg)
            pep.append(self.median)
            pep.append(self.st_deviation)

        elif mode == "label":
            for i in range(len(self.count_dict)):
                pep.append(self.count_dict[i])
            for i in range(len(self.peak_area_dict)):
                pep.append(self.peak_area_dict[i])
            for i in range(len(self.peak_intensity_dict)):
                pep.append(self.peak_intensity_dict[i])
            for i in range(len(self.rt_seconds_dict)):
                pep.append(self.rt_seconds_dict[i])
            for i in range(len(self.ion_dict)):
                pep.append(self.ion_dict[i])
        pep.append(len(self.in_file))
        pep.append(self.protein_count)
        pep.append(self.count_psm_heavy)
        pep.append(self.count_psm_light)
        return pep

    def _dict_to_list_int(self):
        l = []
        for i in range(len(self.ratio_dict)):
            curr = self.ratio_dict[i]
            if curr == "0 dev 0" or curr == "num dev 0" or curr =="":
                continue
            else:
                l.append(self.ratio_dict[i])
        return l

    def _calc_all(self):
        ratio_list = self._dict_to_list_int()
        if len(ratio_list) > 0:
            self.avg = statistics.mean(ratio_list)
            self.median = statistics.median(ratio_list)
            if len(ratio_list) > 1:
                self.st_deviation = statistics.stdev(ratio_list)

    def update_in_file(self,i):
        self.in_file.add(i)
