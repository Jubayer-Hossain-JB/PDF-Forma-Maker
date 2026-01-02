from PyPDF2 import PdfReader, PdfWriter, PageObject, Transformation
import math
from os.path import basename, dirname, join

class PdfStack():
    def init_step(self, input):
        self.reader = PdfReader(input)
        self.width = float(self.reader.pages[0].mediabox.width)
        self.height = float(self.reader.pages[0].mediabox.height)
        self.writer = PdfWriter()
        self.page_count = len(self.reader.pages)
    
    def save_close(self, file_name):
        self.writer.add_metadata(self.reader.metadata)
        saved_file = join(dirname(file_name), "ready_layout "+basename(file_name))
        self.writer.write(saved_file)
        self.writer.close()
        

    def side_pages(self, job):
        new_pages = []
        
        for i in range(len(job)//2):   
            page_1 = job[i]
            page_2 = job[-i-1]
            if i%2 == 1:
                new_pages.append([page_2, page_1])
            else:
                new_pages.append([page_1, page_2])
                
        return new_pages
    
    def down_pages(self, job):
        new_pages = []
        for i in range(len(job)//2):
            page_1 = job[i]
            page_2 = job[-i-1]
            new_pages.append([page_2, page_1])
        return new_pages
        
    def layout4(self,input):
        self.init_step(input)
        valid_sheet = math.ceil(self.page_count/4)*4
        for i in range(valid_sheet//4):
            last_range = (i+1)*4
            if last_range>self.page_count:
                last = [PageObject.create_blank_page(width=self.width, height=self.height) for j in range(last_range-self.page_count)]
                for j in self.reader.pages[i*4:]: last.append(j)
                new_pages = self.side_pages(last)
            else: new_pages = self.side_pages(self.reader.pages[i*4:(i+1)*4]) 
            for p in new_pages:
                page = PageObject.create_blank_page(width=self.width*2, height=self.height)
                page.merge_page(p[0])
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(p[1])
                self.writer.add_page(p)  
        del new_pages
        del self.reader
        self.save_close(input)

    def layout8(self, input):
        self.init_step(input)
        valid_sheet = math.ceil(self.page_count/8)*8

        for i in range(valid_sheet//8):
            last_range = (i+1)*8
            if last_range>self.page_count:
                last = [PageObject.create_blank_page(width=self.width, height=self.height) for j in range(last_range-self.page_count)]
                for j in self.reader.pages[i*8:]: last.append(j)
                new_pages = self.side_pages(last)

            else:
                new_pages = self.side_pages(self.reader.pages[i*8:(i+1)*8])  

            new_pages = self.down_pages(new_pages)

                
            for p in new_pages:
                page = PageObject.create_blank_page(width=self.width*2, height=self.height*2)
                page.merge_page(p[0][0]) 
                page.add_transformation(Transformation().translate(tx=self.width))               
                page.merge_page(p[0][1])
                page.add_transformation(Transformation().rotate(180).translate(tx=self.width, ty=self.height*2))
                page.merge_page(p[1][0])
                page.add_transformation(Transformation().translate(tx=self.width))
                page.merge_page(p[1][1])
                self.writer.add_page(page)  
        self.save_close(input)
        del new_pages
        del last_range
        del self.reader

    def layout16(self, input):
        print('yes')
        self.init_step(input)
        valid_sheet = math.ceil(self.page_count/16)*16
        last_new_doc = []
        for i in range(valid_sheet//16):
            last_range = (i+1)*16
            if last_range>self.page_count:
                last = [PageObject.create_blank_page(width=self.width, height=self.height) for j in range(last_range-self.page_count)]
                for j in self.reader.pages[i*16:]: last.append(j)
                new_pages = self.side_pages(last)

            else:
                new_pages = self.side_pages(self.reader.pages[i*16:(i+1)*16])  

            new_pages = self.down_pages(new_pages)
            new_pages = self.side_pages(new_pages)
        for p in new_pages:
            page = PageObject().create_blank_page(width=self.width*4, height=self.height*2)
            page.merge_page(p[1][0][0])
            page.add_transformation(Transformation().translate(tx=self.width))
            page.merge_page(p[1][0][1])
            page.add_transformation(Transformation().translate(tx=self.width))
            page.merge_page(p[0][0][0])
            page.add_transformation(Transformation().translate(tx=self.width))
            page.merge_page(p[0][0][1])
            page.add_transformation(Transformation().rotate(180).translate(tx=self.width, ty=self.height*2))
            page.merge_page(p[0][1][0])
            page.add_transformation(Transformation().translate(tx=self.width))
            page.merge_page(p[0][1][1])
            page.add_transformation(Transformation().translate(tx=self.width))
            page.merge_page(p[1][1][0])
            page.add_transformation(Transformation().translate(tx=self.width))
            page.merge_page(p[1][1][1])
            self.writer.add_page(page)
        self.save_close(input)
        del new_pages
        del last_range
        del last_new_doc
        del self.reader


