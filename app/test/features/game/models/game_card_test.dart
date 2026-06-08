import 'package:flutter_test/flutter_test.dart';
import 'package:meditation_companion/features/game/models/game_card.dart';

void main() {
  group('GameCard', () {
    test('default flags are false', () {
      const card = GameCard(id: 1, symbol: '🌸');

      expect(card.id, 1);
      expect(card.symbol, '🌸');
      expect(card.isFlipped, isFalse);
      expect(card.isMatched, isFalse);
    });

    group('copyWith', () {
      test('updates only isFlipped and preserves other fields', () {
        const card = GameCard(id: 3, symbol: '🍃');

        final updated = card.copyWith(isFlipped: true);

        expect(updated.id, 3);
        expect(updated.symbol, '🍃');
        expect(updated.isFlipped, isTrue);
        expect(updated.isMatched, isFalse);
      });

      test('updates only isMatched and preserves other fields', () {
        const card = GameCard(id: 4, symbol: '🌊');

        final updated = card.copyWith(isMatched: true);

        expect(updated.id, 4);
        expect(updated.symbol, '🌊');
        expect(updated.isFlipped, isFalse);
        expect(updated.isMatched, isTrue);
      });

      test('with no arguments preserves all fields', () {
        const card = GameCard(
          id: 5,
          symbol: '🌙',
          isFlipped: true,
          isMatched: true,
        );

        final copy = card.copyWith();

        expect(copy, equals(card));
        expect(copy.id, 5);
        expect(copy.symbol, '🌙');
        expect(copy.isFlipped, isTrue);
        expect(copy.isMatched, isTrue);
      });
    });

    group('Equatable equality', () {
      test('two cards with the same fields are equal', () {
        const a = GameCard(
          id: 2,
          symbol: '☀️',
          isFlipped: true,
          isMatched: false,
        );
        const b = GameCard(
          id: 2,
          symbol: '☀️',
          isFlipped: true,
          isMatched: false,
        );

        expect(a, equals(b));
        expect(a.hashCode, equals(b.hashCode));
      });

      test('differ when id differs', () {
        const a = GameCard(id: 1, symbol: '🪷');
        const b = GameCard(id: 2, symbol: '🪷');

        expect(a, isNot(equals(b)));
      });

      test('differ when symbol differs', () {
        const a = GameCard(id: 1, symbol: '🪷');
        const b = GameCard(id: 1, symbol: '🕯️');

        expect(a, isNot(equals(b)));
      });

      test('differ when isFlipped differs', () {
        const a = GameCard(id: 1, symbol: '⛰️');
        const b = GameCard(id: 1, symbol: '⛰️', isFlipped: true);

        expect(a, isNot(equals(b)));
      });

      test('differ when isMatched differs', () {
        const a = GameCard(id: 1, symbol: '⛰️');
        const b = GameCard(id: 1, symbol: '⛰️', isMatched: true);

        expect(a, isNot(equals(b)));
      });

      test('props contains all four fields', () {
        const card = GameCard(
          id: 7,
          symbol: '🌸',
          isFlipped: true,
          isMatched: true,
        );

        expect(card.props, [7, '🌸', true, true]);
      });
    });
  });
}
