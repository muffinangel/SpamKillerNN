Wersja csv01 zawiera:
*2497 rekord�w, kt�re nie s� spamem z pliku 20030228_easy_ham.tar.bz2
*1290 rekord�w, kt�re s� spamem z pliku 20050311_spam_2.tar.bz2
Cz�� mi si� nie wczyta�a - sprawdz� to p�niej dlaczego dok�adnie. Mo�na by te� dorzuci� w kolejnych wersjach pliki z reszty.

Format danych:
is_spam, from, subject, is_formatted, message
*Po ka�dym rekordzie poza ostatnim jest \n, ale mo�e te� by� on w �rodku wiadomo�ci
*is_spam i is_formatted przyjmuje warto�ci '0' i '1' (fa�sz i prawda) - jako teskt!
*from, subject i message s� w cudzys�owiach "

Kod importdata.py nie jest jeszcze ostateczn� wersj� tego kodu.