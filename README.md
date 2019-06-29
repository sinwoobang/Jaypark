# Jaypark [![Build Status](https://travis-ci.com/sinwoobang/Jaypark.svg?token=s64m3rayQnZ6TWPqxtrG&branch=master)](https://travis-ci.com/sinwoobang/Jaypark)
Twitter-like service powered by Django and Graph Database

### Neo4j: Graphs for Everyone
<img src="https://go.neo4j.com/rs/710-RRC-335/images/neo4j_logo.png?_ga=2.73466580.718215210.1555340602-745702593.1554483956" width="300" height="125"><br>

Jaypark uses Graph Database to implement Social Network.<br>
[Neo4j](https://github.com/neo4j/neo4j), the main graph database supports various built-in features.

### Getting Started
Step 0. Install [MySQL 5.7](https://dev.mysql.com/downloads/windows/installer/5.7.html) and [Neo4j](https://neo4j.com/download-center/).

Step 1. Download Backend Dependencies
```bash
$ pip install -r requirements/dev.txt

```


Step 2. Download Frontend Dependencies
```bash
$ bower install

```

Step 3. Runserver
```bash
$ python manage.py runserver

```
<img src="https://d2xnludi9sh0zl.cloudfront.net/photo/profile/f19a02702d344730b39bd350ac04d237">

Run Test Code
```bash
$ coverage run --source='.' manage.py test

```
<img src="https://d2xnludi9sh0zl.cloudfront.net/photo/profile/aeffd787e54445d8a44aef8a083b580d">

Check Test Coverage
```bash
$ coverage report

```
<img src="https://d2xnludi9sh0zl.cloudfront.net/photo/profile/432f264d60fe4e5885fe007995c68825">

### Contribution Guide
* **Coding Convention**: Jaypark follows [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/). Please be careful about it.

* **Backend Dependency**: Backend Dependencies are fully listed on the folder `requirements`. You have to add a library to the list if you inject it into the code.

* **Frontend Dependency**: Frontend Dependencies are fully listed on `bower.json`. You have to add a library to the list if you inject it into the code.

* **Test Code**: You have to add test code if you code something, or Travis CI would raise an error. Test Code is located on test.py of each package.

### What does Jaypark mean?
[Jay Park](https://rocnation.com/jay-park/) is my favorite artist and the first Asian singer to sign with [Roc Nation](https://rocnation.com/).<br>
<br><img src="https://www.allkpop.com/upload/2018/05/af_org/28173717/Jay-Park.jpg" width="500">

