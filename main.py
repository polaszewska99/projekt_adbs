from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_reader(self, reader_name, reader_surname):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_and_return_reader, reader_name, reader_surname
            )

    @staticmethod
    def _create_and_return_reader(tx, reader_name, reader_surname):
        query = (
            """
            CREATE(r1:Reader {name: $reader_name, surname: $reader_surname})
            """
        )
        result = tx.run(query, reader_name=reader_name, reader_surname=reader_surname)
        try:
            return [{"r1": row["r1"]["name"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_author(self, author_name, author_surname):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_and_return_author, author_name, author_surname
            )

    @staticmethod
    def _create_and_return_author(tx, author_name, author_surname):
        query = (
            """
            CREATE(a1:Author {name: $author_name, surname: $author_surname})
            """
        )
        result = tx.run(query, author_name=author_name, author_surname=author_surname)
        try:
            return [{"r1": row["r1"]["name"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_publisher(self, publisher_name):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_and_return_publisher, publisher_name
            )

    @staticmethod
    def _create_and_return_publisher(tx, publisher_name):
        query = (
            """
            CREATE(p:Publisher {name: $publisher_name})
            """
        )
        result = tx.run(query, publisher_name=publisher_name)
        try:
            return [{"r1": row["r1"]["name"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_book(self, book_name, book_years, book_category, author_name, author_surname, publisher_name):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_and_return_book, book_name, book_years, book_category, author_name, author_surname, publisher_name
            )

    @staticmethod
    def _create_and_return_book(tx, book_name, book_years, book_category, author_name, author_surname, publisher_name):
        query = (
            """
            MATCH((a:Author {name: $author_name, surname: $author_surname})),
            ((p:Publisher {name: $publisher_name}))
            CREATE (a)-[:WROTE]->(b:Book {name: $book_name, years: $book_years, category: $book_category})<-[:PUBLISH]-(p)
            """
        )
        result = tx.run(query, book_name=book_name, book_years=book_years, book_category=book_category,
                        author_name=author_name, author_surname=author_surname, publisher_name=publisher_name)
        try:
            return [{"b1": row["b1"]["name"], "a1": row["a1"]["name"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_relation_book_reader(self, person_name, person_surname, mark, book_name):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_relation_book_reader, person_name, person_surname, mark, book_name
            )

    @staticmethod
    def _create_relation_book_reader(tx, person_name, person_surname, mark, book_name):
        query = (
            """
            MATCH (r: Reader {name: $person_name, surname: $person_surname}), (b: Book {name: $book_name})
            MERGE (r)-[rel:READ {mark: $mark}]->(b)
            RETURN r, rel, b
            """
        )
        result = tx.run(query, person_name=person_name, mark=mark, person_surname=person_surname, book_name=book_name)
        try:
            return [{"r": row["r"]["name"], "b": row["b"]["name"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_all_authors_books(self, author_name, author_surname):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_all_authors_books, author_name, author_surname
            )
            print(author_name, author_surname, "books:")
            i = 1
            for row in result:
                print(i, ". {row}".format(row=row))
                i = i+1

    @staticmethod
    def _find_all_authors_books(tx, author_name, author_surname):
        query = (
            """
            MATCH (auth: Author)-[:WROTE]->(authBooks)
            WHERE auth.name = $author_name AND auth.surname = $author_surname
            RETURN authBooks.name AS name
            """
        )
        result = tx.run(query, author_name=author_name, author_surname=author_surname)
        return [row["name"] for row in result]

    def other_read_also(self, book_name):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._other_read_also, book_name
            )
            print("Other users read also: ")
            i = 1
            for row in result:
                print(i, ". {row}".format(row=row))
                i = i+1

    @staticmethod
    def _other_read_also(tx, book_name):
        query = (
            """
            MATCH (b:Book {name: $book_name})
            OPTIONAL MATCH (b)<-[:READ]-(reader)-[r:READ]->(other_book)
            RETURN other_book.name AS title, count(*) AS occurance
            ORDER BY occurance
            DESC 
            """
        )
        result = tx.run(query, book_name=book_name)
        return [row for row in result]

    def find_book_by_year_and_category(self, year_since_book_created, year_to_book_created, category):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_book_by_year_and_category, year_since_book_created, year_to_book_created, category
            )
            print("Books you are looking for: ")
            i = 1
            for row in result:
                print(i, ". {row}".format(row=row))
                i = i+1

    @staticmethod
    def _find_book_by_year_and_category(tx, year_since_book_created, year_to_book_created, category):
        query = (
            """
            MATCH (b:Book {category: $category})
            WHERE $year_to_book_created >= b.years >= $year_since_book_created 
            RETURN b.name AS title, b.years AS year
            ORDER BY year
            """
        )
        result = tx.run(query, year_since_book_created=year_since_book_created, year_to_book_created=year_to_book_created, category=category)
        return [row for row in result]

    def best_book(self):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._best_book
            )
            print("Books you are looking for: ")
            i = 1
            for row in result:
                print(i, ". {row}".format(row=row))
                i = i+1

    @staticmethod
    def _best_book(tx):
        query = (
            """
            MATCH ()-[relation:READ]->(book:Book)
            WITH book, avg(relation.mark) AS mark
            SET book += {MeanMark:mark}
            RETURN book.name, mark
            ORDER BY mark
            DESC 
            LIMIT 3
            """
        )
        result = tx.run(query)
        return [row for row in result]

    def how_many_books_publisher(self):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._how_many_books_publisher
            )
            print("Publishers: ")
            i = 1
            for row in result:
                print(i, ". {row}".format(row=row))
                i = i+1

    @staticmethod
    def _how_many_books_publisher(tx):
        query = (
            """
            MATCH (p1:Publisher)-[r:PUBLISH]->(b:Book)
            RETURN p1.name, count(b)
            """
        )
        result = tx.run(query)
        return [row for row in result]

    def set_literary_period_for_book(self):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._set_literary_period_for_book
            )
            print("Books and literary periods ")
            i = 1
            for row in result:
                print(i, ". {row}".format(row=row))
                i = i+1

    @staticmethod
    def _set_literary_period_for_book(tx):
        query = (
            """
            MATCH(b:Book)
            CALL apoc.do.case([
            b.years >= 1822 AND b.years < 1863, 'SET b.period = "romantyzm" RETURN b',
            b.years >= 1863 AND b.years < 1890, 'SET b.period = "pozytywizm" RETURN b',
            b.years >= 1890 AND b.years < 1918, 'SET b.period = "Młoda Polska" RETURN b',
            b.years >= 1918 AND b.years < 1939, 'SET b.period = "XX-lecie międzywojenne" RETURN b'],
            'SET b.period = "literatura współczesna" RETURN b', {b:b})
            YIELD value
            RETURN value.b.name AS title, value.b.years AS year,
            value.b.period AS LiteraryPeriod 
            ORDER BY year
            """
        )
        result = tx.run(query)
        return [row for row in result]

    def set_literary_period_description(self):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._set_literary_period_description
            )
            print("Books and literary periods description")
            i = 1
            for row in result:
                print(i, ". {row}".format(row=row))
                i = i+1

    @staticmethod
    def _set_literary_period_description(tx):
        query = (
            """
            MATCH(b:Book)
            CALL apoc.case([
            b.period = "romantyzm", 'RETURN "Romantyzm wywodzi się z rewolucji francuskiej, opartej na haśle wolność, równość, braterstwo. W tej epoce literaci często skupiali się na uczuciach i wolności."
            AS description',
            b.period = "pozytywizm", 'RETURN "Pozytywizm z założenia opierał się na wiedzy naukowej oraz odrzuceniem religijności."
            AS description',
            b.period = "Młoda Polska", 'RETURN "Młoda Polska promowała swobodę wyrażania uczuć i ekspresjonizm."
            AS description',
            b.period = "XX-lecie międzywojenne", 'RETURN "Okres między dwoma najtragiczniejszymi wojnami w dziejach ludzkości obfitował w wysyp idei, poglądów i postaw."
            AS description',
            b.period = "literatura współczesna", 'RETURN "W praktyce od czasów II wojny literatura wymknęła się wszelkim ramom i nie ma dominujących nurtów, choć mocno ewoluowała w stronę rozrywki."
            AS description'],
            '', {b:b})
            YIELD value
            RETURN b.name AS title, b.years AS year,
            b.period AS LiteraryPeriod, value.description AS LiteraryPeriodDescription
            ORDER BY year
            """
        )
        result = tx.run(query)
        return [row for row in result]

    def get_similar_users(self, reader_name, reader_surname):
        with self.driver.session() as session:
            session.write_transaction(
                self._similarity_create_project
            )
            session.write_transaction(
                self._similarity_mutate
            )
            result_mean_similarity = session.write_transaction(
                self._similarity_knn_write
            )
            result_similar_readers = session.read_transaction(
                self._similarity_query_all_similarities
            )
            result_recommend_by_similarity = session.read_transaction(
                self._similarity_query_with_recommendation, reader_name, reader_surname
            )
            print("Mean similarity for the graph: ")
            for row in result_mean_similarity:
                print("{row}".format(row=row))

            print("Similar readers: ")
            i = 1
            for row in result_similar_readers:
                print(i, ". {row}".format(row=row))
                i = i+1

            print("For %s %s is recommended: " % (reader_name, reader_surname))
            i = 1
            for row in result_recommend_by_similarity:
                print(i, ". {row}".format(row=row))
                i = i + 1

            session.write_transaction(
                self._similarity_delete_graph
            )

    @staticmethod
    def _similarity_create_project(tx):
        query = (
            """
            CALL gds.graph.project(
            'read_books',
            ['Reader','Book'],
            {
                READ: {
                orientation: 'UNDIRECTED',
                properties: 'mark'
                }   
            }
            )
            """
        )
        result = tx.run(query)
        return [row for row in result]

    @staticmethod
    def _similarity_mutate(tx):
        query = (
            """
            CALL gds.fastRP.mutate('read_books',
            {
                embeddingDimension: 5,
                randomSeed: 42,
                mutateProperty: 'embedding',
                relationshipWeightProperty: 'mark',
                iterationWeights: [1, 1]
            }
            )
            YIELD nodePropertiesWritten
            """
        )
        result = tx.run(query)
        return [row for row in result]

    @staticmethod
    def _similarity_knn_write(tx):
        query = (
            """
            CALL gds.knn.write('read_books', {
                topK: 2,
                nodeProperties: ['embedding'],
                randomSeed: 42,
                concurrency: 1,
                sampleRate: 1.0,
                deltaThreshold: 0.0,
                writeRelationshipType: "SIMILAR",
                writeProperty: "score"
            })
            YIELD nodesCompared, relationshipsWritten, similarityDistribution
            RETURN nodesCompared, relationshipsWritten, similarityDistribution.mean as meanSimilarity
            """
        )
        result = tx.run(query)
        return [row for row in result]

    @staticmethod
    def _similarity_query_all_similarities(tx):
        query = (
            """
            MATCH (n:Reader)-[r:SIMILAR]->(m:Reader)
            WHERE r.score > 0.8
            RETURN n.name, n.surname as reader1, m.name, m.surname as reader2, r.score as similarity
            ORDER BY similarity DESCENDING, reader1, reader2
            """
        )
        result = tx.run(query)
        return [row for row in result]

    @staticmethod
    def _similarity_query_with_recommendation(tx, reader_name, reader_surname):
        query = (
            """
            MATCH (n:Reader{name: $reader_name, surname: $reader_surname})-[r:SIMILAR]->(m:Reader)-[:READ]->(b:Book)
            WITH collect({name:b.name, score:r.score}) as BooksFromSimilarities 
            UNWIND BooksFromSimilarities as RecommendedBooks
            RETURN RecommendedBooks.name as name, avg(RecommendedBooks.score) as score
            order by score DESCENDING
            LIMIT 5
            """
        )
        result = tx.run(query, reader_name=reader_name, reader_surname=reader_surname)
        return [row for row in result]

    @staticmethod
    def _similarity_delete_graph(tx):
        query = (
            """
            CALL gds.graph.drop('read_books') YIELD graphName;
            """
        )
        result = tx.run(query)
        return [row for row in result]

    def delete_reader(self, reader_name, reader_surname):
        with self.driver.session() as session:
            session.write_transaction(
                self._delete_reader, reader_name, reader_surname
            )

    @staticmethod
    def _delete_reader(tx, reader_name, reader_surname):
        query = (
            """
            MATCH (r:Reader {name: $reader_name, surname: $reader_surname})
            DETACH DELETE r
            """
        )
        result = tx.run(query, reader_name=reader_name, reader_surname=reader_surname)
        try:
            return [{"r1": row["r1"]["name"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def best_author(self):
        with self.driver.session() as session:
            session.write_transaction(
                self._set_book_amount
            )
            session.write_transaction(
                self._set_reader_amount
            )
            result = session.write_transaction(
                self._set_avg_mark_books
            )
            print("Best authors: ")
            i = 1
            for row in result:
                print(i, ". {row}".format(row=row))
                i = i + 1

    @staticmethod
    def _set_book_amount(tx):
        query = (
            """
            MATCH (author:Author)-[:WROTE]->(book:Book) 
            WITH author, count(book) AS bookAmount
            SET author +={BookAmount:bookAmount}
            """
        )
        result = tx.run(query)
        return [row for row in result]

    @staticmethod
    def _set_reader_amount(tx):
        query = (
            """
            MATCH (author:Author)-[:WROTE]->(book:Book)<-[r:READ]-(reader:Reader)
            WITH author, count(reader) AS readerAmount
            SET author +={ReaderAmount:readerAmount}
            """
        )
        result = tx.run(query)
        return [row for row in result]

    @staticmethod
    def _set_avg_mark_books(tx):
        query = (
            """
            MATCH (author:Author)-[:WROTE]->(book:Book)<-[r:READ]-(reader:Reader)
            WITH author, sum(book.MeanMark)/author.BookAmount AS score
            SET author +={AvgMarkBook:score}
            RETURN author.name, author.surname, author.BookAmount, author.ReaderAmount, round(author.AvgMarkBook, 2) AS rate
            ORDER BY rate DESCENDING
            """
        )
        result = tx.run(query)
        return [row for row in result]

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "mybase"
    app = App(uri, user, password)
    app.best_author()
    #app.get_similar_users("Natalia", "Krawczyk")
    #app.set_literary_period_description()
    #app.set_literary_period_for_book()
    #app.how_many_books_publisher()
    #app.best_book()
    #app.find_all_authors_books('Lucy', 'Montgomery')
    #app.other_read_also('Ania z Zielonego wzgórza')
    #app.find_book_by_year_and_category(1950, 2000, 'fantasy')

    #app.create_relation_book_reader('Natalia', 'Krawczyk', 4.0, 'Opowieść o dwóch miastach')

    #app.create_reader("Alicja", "Polaszewska")
    #app.delete_reader("Alicja", "Polaszewska")

    '''
    #Authors
    app.create_author('Lucy', 'Montgomery')
    app.create_author('Magdalena', 'Witkiewicz')
    app.create_author('John', 'Steinbeck')
    app.create_author('J.R.R.', 'Tolkien')
    app.create_author('J.D.', 'Salinger')
    app.create_author('J.K.', 'Rowling')
    app.create_author('Stephen', 'King')
    app.create_author('Graham', 'Masterton')
    app.create_author('Karol', 'Dickens')
    app.create_author('Paulo', 'Coelho')
    app.create_author('Antoine', 'Saint-Exupéry')

    #Publishers
    app.create_publisher('PWN')
    app.create_publisher('Sowa')
    app.create_publisher('Gordon')
    app.create_publisher('Radkom')
    
    # BOOKS
    app.create_book('Ania z Zielonego wzgórza', 1908, 'obyczajowe', 'Lucy', 'Montgomery', 'PWN')
    app.create_book('Ania z Avonlea', 1909, 'obyczajowe', 'Lucy', 'Montgomery', 'PWN')
    app.create_book('Dziewczę z sadu ', 1910, 'obyczajowe', 'Lucy', 'Montgomery', 'PWN')
    app.create_book('Historynka', 1911, 'obyczajowe', 'Lucy', 'Montgomery', 'PWN')
    app.create_book('Złocista droga', 1913, 'obyczajowe', 'Lucy', 'Montgomery', 'PWN')
    app.create_book('Ania na Uniwersytecie', 1915, 'obyczajowe', 'Lucy', 'Montgomery', 'PWN')
    app.create_book('Władca Pierścieni. Drużyna Pierścienia', 1954, 'fantasy', 'J.R.R.', 'Tolkien', 'Sowa')
    app.create_book('Władca Pierścieni. Dwie wieże', 1954, 'fantasy', 'J.R.R.', 'Tolkien', 'Sowa')
    app.create_book('Władca Pierścieni. Powrót króla', 1955, 'fantasy', 'J.R.R.', 'Tolkien', 'Sowa')
    app.create_book('Władca Pierścieni. Drużyna Pierścienia', 1954, 'fantasy', 'J.R.R.', 'Tolkien', 'Sowa')
    app.create_book('Hobbit, czyli tam i z powrotem', 1937, 'fantasy', 'J.R.R.', 'Tolkien', 'Sowa')
    app.create_book('Buszujący w zbożu', 1951, 'realizm', 'J.D.', 'Salinger', 'Gordon')
    app.create_book('Dziewięć opowiadań', 1953, 'realizm', 'J.D.', 'Salinger', 'Gordon')
    app.create_book('Harry Potter i kamień Filozoficzny', 1997, 'fantasy', 'J.K.', 'Rowling', 'PWN')
    app.create_book('Harry Potter i Komnata Tajemnic', 1998, 'fantasy', 'J.K.', 'Rowling', 'PWN')
    app.create_book('Harry Potter i więzień Azkabanu', 1999, 'fantasy', 'J.K.', 'Rowling', 'PWN')
    app.create_book('Harry Potter i Czara Ognia', 2000, 'fantasy', 'J.K.', 'Rowling', 'PWN')
    app.create_book('Harry Potter i Zakon Feniksa', 2003, 'fantasy', 'J.K.', 'Rowling', 'PWN')
    app.create_book('Harry Potter i Książę Półkrwi', 2005, 'fantasy', 'J.K.', 'Rowling', 'PWN')
    app.create_book('Harry Potter i Insygnia Śmierci', 2007, 'fantasy', 'J.K.', 'Rowling', 'PWN')
    app.create_book('Carrie', 1974, 'horror', 'Stephen', 'King', 'Gordon')
    app.create_book('Lśnienie', 1977, 'horror', 'Stephen', 'King', 'Gordon')
    app.create_book('Miasteczko Salem', 1975, 'horror', 'Stephen', 'King', 'Gordon')
    app.create_book('Martwa strefa', 1979, 'horror', 'Stephen', 'King', 'Gordon')
    app.create_book('Wyklęty', 1983, 'horror', 'Graham', 'Masterton', 'Gordon')
    app.create_book('Opowieść o dwóch miastach', 1859, 'historyczna', 'Karol', 'Dickens', 'Gordon')
    app.create_book('Alchemik', 1943, 'powiastka filozoficzna', 'Paulo', 'Coelho', 'Radkom')
    app.create_book('Mały Książę', 1943, 'powiastka filozoficzna', 'Antoine', 'Saint-Exupéry', 'Radkom')
    app.create_book('Córka generała', 2022, 'obyczajowe', 'Magdalena', 'Witkiewicz', 'Sowa')
    app.create_book('Ulica Nadbrzezna', 1972, 'obyczajowe', 'John', 'Steinbeck', 'Sowa')

    # READAERS
    app.create_reader('Jan', 'Kowalski')
    app.create_reader('Karolina', 'Piasecka')
    app.create_reader('Natalia', 'Krawczyk')
    app.create_reader('Krystian', 'Tomczyk')
    app.create_reader('Janina', 'Stolarek')
    app.create_reader('Jakub', 'Kawka')
    app.create_reader('Jan', 'Kownacki')
    app.create_reader('Alicja', 'Antecka')
    app.create_reader('Julia', 'Kamyk')
    app.create_reader('Kryspin', 'Nowak')
    app.create_reader('Grzegorz', 'Zwierzyński')

    # READERS AND BOOKS
    app.create_relation_book_reader('Jan', 'Kowalski', 9, 'Ania z Zielonego wzgórza')
    app.create_relation_book_reader('Karolina', 'Piasecka', 9.5, 'Ania z Zielonego wzgórza')
    app.create_relation_book_reader('Natalia', 'Krawczyk', 7, 'Ania z Zielonego wzgórza')
    app.create_relation_book_reader('Julia', 'Kamyk', 8.5, 'Ania z Zielonego wzgórza')
    app.create_relation_book_reader('Karolina', 'Piasecka', 6.0, 'Ania z Avonlea')
    app.create_relation_book_reader('Karolina', 'Piasecka', 7.0, 'Ania na Uniwersytecie')
    app.create_relation_book_reader('Julia', 'Kamyk', 10, 'Ania z Avonlea')
    app.create_relation_book_reader('Julia', 'Kamyk', 5.0, 'Ania na Uniwersytecie')
    app.create_relation_book_reader('Karolina', 'Piasecka', 9.5, 'Buszujący w zbożu')
    app.create_relation_book_reader('Natalia', 'Krawczyk', 8, 'Buszujący w zbożu')

    app.create_relation_book_reader('Grzegorz', 'Zwierzyński', 8, 'Harry Potter i kamień Filozoficzny')
    app.create_relation_book_reader('Grzegorz', 'Zwierzyński', 8, 'Harry Potter i Komnata Tajemnic')
    app.create_relation_book_reader('Julia', 'Kamyk', 6.5, 'Harry Potter i kamień Filozoficzny')
    app.create_relation_book_reader('Julia', 'Kamyk', 8.5, 'Harry Potter i Komnata Tajemnic')
    app.create_relation_book_reader('Julia', 'Kamyk', 7.5, 'Harry Potter i więzień Azkabanu')
    app.create_relation_book_reader('Julia', 'Kamyk', 8.5, 'Harry Potter i Czara Ognia')
    app.create_relation_book_reader('Julia', 'Kamyk', 5.5, 'Opowieść o dwóch miastach')
    app.create_relation_book_reader('Jan', 'Kownacki', 6.5, 'Opowieść o dwóch miastach')
    app.create_relation_book_reader('Jan', 'Kownacki', 8.5, 'Mały Książę')
    app.create_relation_book_reader('Jan', 'Kownacki', 6.5, 'Alchemik')
    app.create_relation_book_reader('Alicja', 'Antecka', 8.5, 'Lśnienie')
    app.create_relation_book_reader('Alicja', 'Antecka', 7.5, 'Carrie')
    app.create_relation_book_reader('Jakub', 'Kawka', 8.5, 'Carrie')
    app.create_relation_book_reader('Jakub', 'Kawka', 6.5, 'Alchemik')
    app.create_relation_book_reader('Kryspin', 'Nowak', 5, 'Opowieść o dwóch miastach')
    app.create_relation_book_reader('Kryspin', 'Nowak', 7.5, 'Buszujący w zbożu')
    app.create_relation_book_reader('Karolina', 'Piasecka', 9.5, 'Córka generała')
    app.create_relation_book_reader('Karolina', 'Piasecka', 5.5, 'Ulica Nadbrzezna')
    '''

    app.close()
