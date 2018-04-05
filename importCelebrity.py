#coding: utf-8

import csv
import os
import pinyin
import random
import mysql.connector
from aip import AipFace
# import collections

from models.Person import Person
from config.Config import Config

csvFilePath = os.getcwd() + '/resource/celebrity/celebrities.csv'
directoryPath = os.getcwd() + '/resource/celebrity/img/'

personList = []


# Step 1. Load celebs from csv file
def parse_csv():
    with open(csvFilePath, newline='', encoding='utf-8') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        for row in csvReader:
            if len(row) == 9:
                newPerson = Person(row[1], row[2], row[3], row[4], row[5], row[6], row[7].encode("utf-8"), row[8], [])
                personList.append(newPerson)
            else:
                print(row[0], row[1])
# print('Totally processed: ', len(personList))


# Step 2. Load image names from img folder
directory = os.fsencode(directoryPath)
validFileType = ["jpg", "jpeg", "png", "gif"]
imageList = []


def attach_img():
    for file in os.listdir(directory):

        file_name = os.fsdecode(file)
        file_type = file_name.split('.')[1]
        if validFileType.__contains__(file_type):
            imageList.append(file_name)

    print('Total images: ', len(imageList))

    # Step 3. Append images to personList

    for person in personList:
        pinyin_name = pinyin.get(person.name, format="strip")
        person.pinyinName = pinyin_name

        for imageName in imageList:
            if imageName.split('.')[0].split('-')[0] == pinyin_name:
                person.images.append(imageName)


# Step 4. Loop personList, upload to Cloud and save to DB
def save_db():

    cnx = mysql.connector.connect(user='root', password='root',
                                  host='127.0.0.1',
                                  database='chbb_facecompare')
    cursor = cnx.cursor()

    insert_celebrity_query = 'insert into `celebrity` values (null, %s, %s, %s, %s, %s, %s, %s)'
    insert_image_query = 'insert into `celebrityImage` values (null, %s, %s, %s, %s)'

    for person in personList:

        person_dob = None
        if person.dob.find('日') > -1:
            person_dob = person.dob.replace('年', '-').replace('月', '-').replace('日', '')

        celebrity_data = (
            person.name, person.gender, person_dob, person.job, person.nationality,
            person.birthplace, person.desc)

        cursor.execute(insert_celebrity_query, celebrity_data)
        celeb_id = cursor.lastrowid

        print(len(person.images), ' images imported')
        for img in person.images:
            image_data = (celeb_id, img.find('child') > -1, img, person.pinyinName + '_' + str(random.randint(1000, 9999)))
            cursor.execute(insert_image_query, image_data)

        print(person.name, ' inserted.')
        cnx.commit()

    cursor.close()
    cnx.close()


# Step 5. Loop images upload to Baidu Cloud
def upload_face():
    male_group_id = 'celebrity_male_test'
    female_group_id = 'celebrity_female_test'

    app_id = Config().get("AipConfig", "APP_ID")
    api_key = Config().get("AipConfig", "API_KEY")
    secret_key = Config().get("AipConfig", "SECRET_KEY")
    client = AipFace(app_id, api_key, secret_key)

    cnx = mysql.connector.connect(user='root', password='root',
                                  host='127.0.0.1',
                                  database='chbb_facecompare')
    cursor = cnx.cursor()
    query_images = 'select c.name, c.gender, ci.imagePath, ci.uid from celebrity c join celebrityImage ci on ci.celebrity_id = c.id;'
    cursor.execute(query_images)

    for (name, gender, imagePath, uid) in cursor:
        group_id = ''
        # print(name, gender, imagePath, uid)
        if gender == '男':
            group_id = male_group_id
        elif gender == '女':
            group_id = female_group_id
        else:
            print(gender)

        image_path = directoryPath + imagePath
        options = {
            "action_type": "replace"
        }
        client.updateUser(uid, name, group_id, get_file_content(image_path), options)
        print(name, gender, 'uploaded.')

    cursor.close()
    cnx.close()

# Util: read image
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def clear_all_faces():

    male_group_id = 'celebrity_male_test'
    female_group_id = 'celebrity_female_test'

    app_id = Config().get("AipConfig", "APP_ID")
    api_key = Config().get("AipConfig", "API_KEY")
    secret_key = Config().get("AipConfig", "SECRET_KEY")
    client = AipFace(app_id, api_key, secret_key)

    options = {
        "start": 0,
        "num": 500
    }
    male_result = client.getGroupUsers(male_group_id, options).get('result')
    female_result = client.getGroupUsers(female_group_id, options).get('result')

    for m in male_result:
        response = client.deleteUser(m.get('uid'))
        print('removed: ', m.get('uid'))
    for f in female_result:
        response = client.deleteUser(f.get('uid'))
        print('removed: ', f.get('uid'))

# Control Whole Process
# parse_csv()
# attach_img()
# save_db()
upload_face()

# clear_all_faces()
