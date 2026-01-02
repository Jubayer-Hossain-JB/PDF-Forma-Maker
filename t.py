def side_pages(job):
    new_pages = []
    
    for i in range(len(job)//2):   
        page_1 = job[i]
        page_2 = job[-i-1]
        if i%2 == 1:
            new_pages.append([page_2, page_1])
        else:
            new_pages.append([page_1, page_2])
            
    return new_pages

def down_pages(job):
    new_pages = []
    for i in range(len(job)//2):
        page_1 = job[i]
        page_2 = job[-i-1]
        new_pages.append([page_2, page_1])
    return new_pages

print(down_pages(side_pages(list(range(8)))))