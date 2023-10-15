% одинарные факты
% расы
:- dynamic imperial/1.
imperial(elysif).
imperial(tullius).
imperial(rikke).
imperial(jianna).
imperial(pantea).

:- dynamic breton/1.
breton(sibilla).
breton(vivienne).
breton(angeline).

:- dynamic nord/1.
nord(folk).
nord(rorlund).
nord(freir).
nord(illdi).
nord(jordis).
nord(jala).

:- dynamic altmer/1.
altmer(viarmo).
altmer(elenven).

:- dynamic argonian/1.
argonian(jaree-ra).
argonian(didja).
argonian(gulum-ei).

%пол
:- dynamic man/1.
man(tullius).
man(folk).
man(rorlund).
man(viarmo).
man(jaree-ra).
man(gulum-ei).

:- dynamic woman/1.
woman(elysif).
woman(rikke).
woman(jianna).
woman(pantea).
woman(sibilla).
woman(vivienne).
woman(angeline).
woman(freir).
woman(illdi).
woman(jordis).
woman(jala).
woman(elenven).
woman(didja).



% предикаты
% золото
:- dynamic septims/2.
septims(elysif, 100000).
septims(tullius, 2000).
septims(rikke, 1500).
septims(jianna, 50).
septims(pantea, 1200).
septims(sibilla, 1000).
septims(vivienne, 20).
septims(angeline, 0).
septims(folk, 1000).
septims(rorlund, 100).
septims(freir, 20).
septims(jordis, 200).
septims(jala, 5).
septims(viarmo, 60).
septims(elenven, 20000).
septims(jaree-ra, 1500).
septims(didja, 1500).
septims(gulum-ei, 1000).
septims(illdi, 10).

% фракции
:- dynamic fraction/2.
fraction(elysif, dominion).
fraction(tullius, dominion).
fraction(rikke, dominion).
fraction(sibilla, dominion).
fraction(elenven, dominion).
fraction(gulum-ei, thiefs).
fraction(pantea, bards).
fraction(viarmo, bards).
fraction(illdi, bards).

% лидеры
leader(elysif, dominion).
leader(gulum-ei, thiefs).
leader(pantea, bards).

% торговые предложения
trade_offer(sibilla, potions, 100).
trade_offer(sibilla, herbs, 40).
trade_offer(folk, house, 40000).
trade_offer(pantea, song, 20).
trade_offer(viarmo, song, 15).
trade_offer(illdi, song, 15).
trade_offer(jala, fruits, 5).
trade_offer(angeline, herbs, 50).
trade_offer(vivienne, potions, 80).
trade_offer(vivienne, herbs, 60).
trade_offer(gulum-ei, information, 1000).
trade_offer(gulum-ei, stolen, 100).

% проверка совместимости рас
are_hatred(X, Y):-
	imperial(X), nord(Y), !;
	imperial(X), breton(Y), !;
	imperial(X), argonian(Y), !;
	nord(X), altmer(Y), !;
	nord(X), argonian(Y), !;
	breton(X), argonian(Y), !;
	altmer(X), nord(Y), !;
	altmer(X), argonian(Y), !.

% проверка союзов
are_allies(X, Y):-
	fraction(X, Z), 
	fraction(Y, Z),
	not(are_hatred(X, Y)).

% проверка возможности покупки
can_purchase(X, Y, Z):-
    septims(X, Money),
    % проверяем наличие межрасовой нетерпимости, которая не позволит продавцу отпускать товары дороже 100 септимов
	(are_hatred(Y, X) ->
		(findall(Trades, (trade_offer(Y, Trades, Z),Z<100,Z=<Money), List),
		(length(List, Length), Length>0 ->
			(write(X), write(' может приобрести у '), write(Y), write(': '), write(List), nl, Z = 'can buy'); (write(X), write(' ничего не может приобрести у '), write(Y), Z = 'cannot buy (race)')
		)
		), !;
    	% союзникам по блоку полагается скидка в 50%
    	(are_allies(X, Y) ->
    	(findall(Trades, (trade_offer(Y, Trades, Z),Z=<Money/2), List),
        (length(List, Length), Length>0 ->
			(write(X), write(' может приобрести со скидкой в 50% у '), write(Y), write(': '), write(List), nl, Z = 'can buy with discont'); (write(X), write(' ничего не может приобрести у '), write(Y), Z = 'cannot buy')
		)    
    )
    ), !;
		(findall(Trades, (trade_offer(Y, Trades, Z),Z=<Money), List),
		(length(List, Length), Length>0 ->
			(write(X), write(' может приобрести у '), write(Y), write(': '), write(List), nl, Z = 'can buy'); (write(X), write(' не хватает денег чтобы приобрести у '), write(Y), Z = 'cannot buy')
		)
		)
	).

% поиск выгодного брака. Чтобы партия состоялась, бюджеты сторон не должны отличаться больше чем в 2 раза.
marriage(X, Y):-
    septims(X, Money1),
    (man(X) ->  
    (findall(Y, (woman(Y),septims(Y, Money2),(Money2/2=<Money1,Money1/2=<Money2,not(are_hatred(Y, X)))), PartyList),
    (length(PartyList, Length), Length>0 ->  
    	(write(X), write(' может жениться на '), write(PartyList), nl, Y = PartyList); (write(X), write(' не может найти себе достойную партию в городе Солитьюд'), nl, Y is 0)
    )
    );
    (findall(Y, (man(Y),septims(Y, Money2),(Money2/2=<Money1,Money1/2=<Money2,not(are_hatred(Y, X)))), PartyList),
    (length(PartyList, Length), Length>0 ->  
    	(write(X), write(' может выйти замуж за '), write(PartyList), nl, Y = PartyList); (write(X), write(' не может найти себе достойную партию в городе Солитьюд'), nl, Y is 0)
    )
    )
    ).

% вступление в новый блок
new_allies(X, Fraction, Z):-
    %проверяем наличие нетерпимости у лидера фракции
    leader(Y, Fraction),
    (are_hatred(Y, X) -> (write(X), write(' не может вступить в фракцию '), write(Fraction), Z is 0);
    	% проверяем наличие текущего блока
    	(fraction(X, OldFract) ->  (retract(fraction(X, OldFract)), assertz(fraction(X, Fraction)), 
                                   write(X), write(' покидает свою фракцию и присоединяется к '), write(Fraction), nl, Z is 1,
                                       % проверка на выход
                                   findall(Mem, fraction(Mem, OldFract), OldList),
                                       write(OldList), nl
                                   );
        	(assertz(fraction(X, Fraction)), write(X), write(' присоединяется к '), write(Fraction), nl, Z is 2)
        )
    ),
    findall(Member, fraction(Member, Fraction), List),
    write(List).

% добавление нового человека
add_human(Name, Race, Sex, Fraction, Gold):-
    (Race=='imperial' ->  (assertz(imperial(Name)));
    (Race=='breton' ->   (assertz(breton(Name)));
    (Race=='nord' ->  (assertz(nord(Name)));
    (Race=='altmer' -> (assertz(altmer(Name)));
    (Race=='argonian' -> (assertz(argonian(Name)));
    (write('Такая раса не обитает в Солитьюде'))
    ))))),
    (Sex=='man' ->  (assertz(man(Name))); (assertz(woman(Name)))),
    (not(Fraction=='') ->  assertz(fraction(Name, Fraction))),
    assertz(septims(Name, Gold)).
    
    


