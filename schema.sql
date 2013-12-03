PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE book (
	id INTEGER NOT NULL, 
	title VARCHAR, 
	PRIMARY KEY (id)
);
CREATE TABLE author (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	PRIMARY KEY (id)
);
CREATE TABLE book_author (
	book_id INTEGER, 
	author_id INTEGER, 
	FOREIGN KEY(book_id) REFERENCES book (id), 
	FOREIGN KEY(author_id) REFERENCES author (id)
);
COMMIT;
