import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:meditation_companion/features/game/repository/game_repository.dart';

void main() {
  group('GameRepository.generateDeck', () {
    test('returns pairCount * 2 cards', () {
      final repository = GameRepository(random: Random(1));

      final deck = repository.generateDeck(pairCount: 4);

      expect(deck, hasLength(8));
    });

    test('default pairCount is 6 (12 cards)', () {
      final repository = GameRepository(random: Random(1));

      final deck = repository.generateDeck();

      expect(deck, hasLength(12));
    });

    test('ids are unique and contiguous 0..n-1', () {
      final repository = GameRepository(random: Random(1));

      final deck = repository.generateDeck(pairCount: 5);
      final ids = deck.map((card) => card.id).toList()..sort();

      expect(ids, [for (var i = 0; i < deck.length; i++) i]);
      expect(ids.toSet(), hasLength(deck.length));
    });

    test('every symbol appears exactly twice', () {
      final repository = GameRepository(random: Random(1));

      final deck = repository.generateDeck(pairCount: 6);

      final counts = <String, int>{};
      for (final card in deck) {
        counts[card.symbol] = (counts[card.symbol] ?? 0) + 1;
      }

      expect(counts.length, 6);
      for (final entry in counts.entries) {
        expect(entry.value, 2, reason: 'symbol ${entry.key} should appear twice');
      }
    });

    test('all cards start unflipped and unmatched', () {
      final repository = GameRepository(random: Random(1));

      final deck = repository.generateDeck(pairCount: 6);

      for (final card in deck) {
        expect(card.isFlipped, isFalse);
        expect(card.isMatched, isFalse);
      }
    });

    group('determinism', () {
      test('same seed yields identical symbol order', () {
        final deckA =
            GameRepository(random: Random(42)).generateDeck(pairCount: 6);
        final deckB =
            GameRepository(random: Random(42)).generateDeck(pairCount: 6);

        final symbolsA = deckA.map((card) => card.symbol).toList();
        final symbolsB = deckB.map((card) => card.symbol).toList();

        expect(symbolsA, equals(symbolsB));
      });

      test('same seed yields identical decks', () {
        final deckA =
            GameRepository(random: Random(7)).generateDeck(pairCount: 4);
        final deckB =
            GameRepository(random: Random(7)).generateDeck(pairCount: 4);

        expect(deckA, equals(deckB));
      });
    });
  });
}
