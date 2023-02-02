# Archeo 2022
Tkinter app for keeping and managing documents from archive resources.

## Content of project
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Application view](#application-view)
* [Functionalities](#functionalities)
* [Inspiration & Sources](#inspiration--sources)
* [Contact](#contact)

## General info
Tkinter App replacing a paper register used to keep records of taking and returning files from the company archive.</br>
Database stores information such as data identifying the case contained in the file, comments, dates of transfers and persons transferring, returning and
responsible for the folder.


## Technologies
<ul>
<li>Python 3.10.5</li>
<li>SQLite 3.37.2</li>
<li>Tkinter</li>
</ul>

## Setup

All libraries used in the App are included with Python 3.10, so you don't need to install any extra packages.</br>
Database is created with the first launch of the app.

To create a desktop App we'll use pyinstaller</br>
First install a package. Run this command in your Terminal:

```commandline
pip install pyinstaller
```

Next step is to create an executable file from the project:
```commandline
pyinstaller --onefile --windowed --icon="graphics/ikona4.ico" main.py
```

New file appears in <code>PROJECT_LOCATION/dist/main.exe</code></br>
</br>
To make it work you need to copy <code>graphics/</code> folder </br>
to <code>dist/</code> or move <code>main.exe</code> to project location.

Now open <code>main.exe</code> and enjoy!

## Application view
<img src="https://user-images.githubusercontent.com/108935246/203978921-c22a5d31-b822-4242-8108-267b43d4ea0d.png" width="40%" height="40%">

<img src="https://user-images.githubusercontent.com/108935246/205458190-f859adb2-4ae9-464e-9b2f-bc6db6c2037d.png" width="40%" height="40%">

<img src="https://user-images.githubusercontent.com/108935246/205460815-2f9f00a2-10ec-4d27-baeb-6d89756c4655.png" width="40%" height="40%">

<img src="https://user-images.githubusercontent.com/108935246/205461008-9651f2e3-f604-4a84-8bb8-944fca5bca27.png" width="40%" height="40%">

## Functionalities
The very first thing you have to do when launch the app is to <b>select the operator</b> on top of the screen.</br>
Only after that all <strong>widgets become unlocked.</strong>

<details>
<summary><b>Pojazd</b></summary>

### Taking the files

Now you can fill the information about taken documents
</br>
![2](https://user-images.githubusercontent.com/108935246/205375869-6c790679-210d-4e92-ae23-b50ec7b77ac3.png)
</br>
<ol>
    <li>    
        <h6>Register plate number - Required</h6>
            <ul>Regex function checks the compliance of the given string with pattern provided in the act.</ul>
            <ul>If there is no validation app show a <b>Warning</b> when trying to save</ul>
    </li>
    <li>
        <h6>Osoba pobierająca (A person taking the files) - Required</h6>
    </li>
    <li>
        <h6>Osoba prowadząca sprawę (A person responsible for taken documents) - Required</h6>
    </li>
    <li>
        <h6>Inna data (Another date) - Optional</h6>
            <ul>Default date is a date and time got when you save the record,<br>
            but sometimes you need to set another date.<br>
            Just check the checkbox and fill date in YYYY-MM-DD format</ul>
    </li>
    <li>
        <h6>Uwagi (Comments) - Optional</h6>
    </li>
</ol>
Once all the forms are filled you can save the record to Database by clicking 'Zastosuj' button.
If something goes wrong (e.g. register plate number don't fit pattern, wrong date format, empty required forms) the app 
show a warning or error.<br>
If everything is ok a confirmation message will be showed underneath the button and record preview appears in a table.

![4](https://user-images.githubusercontent.com/108935246/205375974-600d6a2d-c299-4512-b5e4-bb982b2bc376.png)
![5](https://user-images.githubusercontent.com/108935246/205376076-bb95c1a0-a912-48ef-bc4b-6f65299ad2cc.png)
</br>
</br>

### Returning the files

![3](https://user-images.githubusercontent.com/108935246/205377515-681403e7-a886-4cd5-a695-aed17d6dee59.png)

To return the files you do similar.
<ol>
    <li>
        <h6>Register plate number - Required</h6>
            <ul>Same validation as previously plus checking if given numer is already taken and <b>NOT RETURNED</b></ul>
    </li>
    <li>
        <h6>Osoba zwracająca (A person returning the files) - Required</h6>
    </li>
    <li>
        <h6>Inna data (Another date) - Optional</h6>
            <ul>Same validation as previously</ul>
    </li>
</ol>

After save by clicking the 'Zastosuj' button you will see the confirmation message and the record preview.

![6](https://user-images.githubusercontent.com/108935246/205380312-596fbeae-0763-4c87-879e-d6747db641cf.png)

![7](https://user-images.githubusercontent.com/108935246/205380316-e96a7dcb-32c1-493a-80a1-e58239b10d47.png)


###### NOTE: 
<ul>You can take files that are returned or haven't been taken</ul>
<ul>You can return only taken files</ul>
<ul>You can take files with invalid pattern after additional confirmation</ul>

</details>

<details>
<summary><b>Kierowca</b></summary>

<br>
    
![9](https://user-images.githubusercontent.com/108935246/205386257-d34a29d3-921e-4fff-b829-281be2ef2b3f.png)

<ol>
    <li>    
        <h6>Nazwisko (Last name) - Required</h6>
    </li>
    <li>    
        <h6>Imię (First name) - Required</h6>
    </li>
    <li>    
        <h6>PESEL (Polish ID) - Required</h6>
            <ul>Valid PESEL number has 11 digits and lights up the form in green. If it's invalid background is red</ul>
    </li>
    <li>    
        <h6>Numer K/K (Qualification Card Number) - Required</h6>
            <ul>It's required but default value is 'B/U' (no permissions) because not all the drivers has a Card.</ul>
    </li>
    <li>
        <h6>Osoba pobierająca (A person taking the files) - Required</h6>
    </li>
    <li>
        <h6>Osoba prowadząca sprawę (A person responsible for taken documents) - Required</h6>
    </li>
    <li>
        <h6>Data urodzenia (birthday date) - Optional</h6>
            <ul>Sometimes people doesn't have a PESEL number. In that case you can use their birthday date</ul>
    </li>
    <li>
        <h6>Inna data (Another date) - Optional</h6>
            <ul>Default date is a date and time got when you save the record,<br>
            but sometimes you need to set another date.<br>
            Just check the checkbox and fill date in YYYY-MM-DD format</ul>
    </li>
    <li>
        <h6>Uwagi (Comments) - Optional</h6>
    </li>
    <li>
        <h6>Żądanie akt (files request) - Optional</h6>
            <ul>There are situation that someone takes the files, and they never return it because of some reasons.<br>
                If you check this box the return date will be filled with this info and looks like returned.</ul>
    </li>
</ol>

Once all the forms are filled you can save the record to Database by clicking 'Zastosuj' button.
If something goes wrong (e.g. PESEL number don't fit pattern, wrong date format, empty required forms) the app 
show a warning or error.</br>
If everything is ok a confirmation message will be showed underneath the button and record preview appears in a table.

![10](https://user-images.githubusercontent.com/108935246/205439866-26163bb6-2937-4953-b6cf-0069b8cce6ee.png)

![11](https://user-images.githubusercontent.com/108935246/205439871-a4d48a2a-ed8a-4a77-82e4-2aff8281ed67.png)

### Returning the files

![14](https://user-images.githubusercontent.com/108935246/205443615-5bd89604-7088-44de-9d81-17bdfbca748b.png)

To return the files you do similar.
<ol>
    <li>
        <h6>PESEL number - Required/Optional*</h6>
            <ul>Same validation as previously plus checking if given numer is already taken and <b>NOT RETURNED</b></ul>
    </li>
    <li>
        <h6>Nr K/K - Required/Optional*</h6>
    </li>
    <li>
        <h6>Osoba zwracająca (A person returning the files) - Required</h6>
    </li>
    <li>
        <h6>Inna data (Another date) - Optional</h6>
            <ul>Same validation as previously</ul>
    </li>
</ol>

After save by clicking the 'Zastosuj' button you will see the confirmation message and the record preview.

![12](https://user-images.githubusercontent.com/108935246/205440422-22307efa-16ea-48f3-ba93-879936e5c427.png)

![13](https://user-images.githubusercontent.com/108935246/205440424-fa578c45-6dbb-4dfa-9afb-1efc1f59d23c.png)

###### NOTE: 
<ul>* - You can return files using only one of these parameters. In that case the second one is not required.</ul>
<ul>** - After fill PESEL or NR K/K, name assigned to that value will be showed between forms 
to make sure you entered them correctly</ul>

</details>

<details>
    <summary><b>Search engine</b></summary>
    <br>
    <ul>You can find any record you want using this search engine. Check the correctness of the data and edit or delete them.</ul>
    <ul>You have many options to chose from to find the record by full or just a part of data.</ul>
    <ul>You can also sort the results by any column ascent and descent.</ul>
    <ul>Above table is a found results counter.</ul>

</details>

## Inspiration & Sources
This App is my original idea to improve productivity in my company and bring the office into the 21st century, to say '<b>goodbye</b>' to old-school paper registries and to say '<b>hello</b>' to computer. Even for pre-retirement employers.

I'm the beginner, so I couldn't write this without help.</br>
My main source of invaluable help was ```Codemy.com``` YouTube Channel</br>
A good documentation of a ```Tkinter``` was also helpfully. 

## Contact
If you have any questions or ideas for development feel free to contact me via email:</br>
```maritn.brzezinski@wp.eu```

### Update
#### Version 1.3 
* Added a checkbox which is set when taken files will not be returned to the archive.