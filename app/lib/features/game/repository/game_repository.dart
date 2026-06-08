import 'dart:math';

import 'package:meditation_companion/features/game/models/game_card.dart';

/// Provides the deck of cards for a memory match game.
///
/// Defined as an interface so a deterministic implementation can be injected
/// in tests (via a seeded [Random]) while production code uses real shuffling.
abstract class IGameRepository {
  /// Builds a shuffled deck containing [pairCount] pairs (so
  /// `pairCount * 2` cards in total), each card assigned a unique id.
  List<GameCard> generateDeck({int pairCount});
}

class GameRepository implements IGameRepository {
  /// Calming, meditation-themed symbols used to build pairs.
  static const List<String> _symbols = [
    '🌸',
    '🍃',
    '🌊',
    '🌙',
    '☀️',
    '🪷',
    '🕯️',
    '⛰️',
  ];

  final Random _random;

  GameRepository({Random? random}) : _random = random ?? Random();

  @override
  List<GameCard> generateDeck({int pairCount = 6}) {
    assert(pairCount > 0, 'pairCount must be positive');
    assert(
      pairCount <= _symbols.length,
      'pairCount cannot exceed ${_symbols.length} available symbols',
    );

    final chosen = _symbols.take(pairCount).toList();
    final symbols = [...chosen, ...chosen]..shuffle(_random);

    return [
      for (var i = 0; i < symbols.length; i++)
        GameCard(id: i, symbol: symbols[i]),
    ];
  }
}
