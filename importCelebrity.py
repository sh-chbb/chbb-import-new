import csv
import os
import pinyin
import requests
import collections

from models.Person import Person

csvFilePath = os.getcwd() + '/resource/celebrity/celebrities.csv'
directoryPath = os.getcwd() + '/resource/celebrity/img/'

personList = []

# Step 1. Load celebs from csv file
with open(csvFilePath, newline='') as csvFile:

    csvReader = csv.reader(csvFile, delimiter=',')
    for row in csvReader:
        newPerson = Person(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        personList.append(newPerson)

# print('Totally processed: ', len(personList))

# Step 2. Load image names from img folder
directory = os.fsencode(directoryPath)
validFileType = ["jpg", "jpeg", "png", "gif"]
imageList = []
matchImageList = []

for file in os.listdir(directory):

    fileName = os.fsdecode(file)
    fileType = fileName.split('.')[1]
    if validFileType.__contains__(fileType):
        imageList.append(fileName)

print('Total images: ', len(imageList))

# Step 3. Append images to personList
totalMatchImages = 0

for person in personList:

    pinyinName = pinyin.get(person.name, format="strip")

    for imageName in imageList:

        if imageName.split('.')[0].split('-')[0] == pinyinName:

            matchImageList.append(imageName)
            person.images.append(imageName)
            totalMatchImages += 1


# Step 4. Loop personList, upload to Cloud and save to DB

