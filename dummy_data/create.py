from faker import Faker

fake = Faker()

with open('dummy_data/dummy_data_large.csv', 'w+') as file:
    file.write('Name,Email,Favorite Color,Phone Number,Country\n')
    for i in range(100000):
        name = fake.name()
        email = fake.email()
        fav_color = fake.color_name()
        phone_number = fake.phone_number()
        country = fake.country()
        file.write(f'{name},{email},{fav_color},{phone_number},{country}\n')


with open('dummy_data/dummy_data_medium.csv', 'w+') as file:
    file.write('Name,Email,Favorite Color,Phone Number,Country\n')
    for i in range(10000):
        name = fake.name()
        email = fake.email()
        fav_color = fake.color_name()
        phone_number = fake.phone_number()
        country = fake.country()
        file.write(f'{name},{email},{fav_color},{phone_number},{country}\n')

with open('dummy_data/dummy_data_small.csv', 'w+') as file:
    file.write('Name,Email,Favorite Color,Phone Number,Country\n')
    for i in range(1000):
        name = fake.name()
        email = fake.email()
        fav_color = fake.color_name()
        phone_number = fake.phone_number()
        country = fake.country()
        file.write(f'{name},{email},{fav_color},{phone_number},{country}\n')
