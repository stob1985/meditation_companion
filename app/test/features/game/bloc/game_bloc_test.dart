import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:meditation_companion/features/game/bloc/game_bloc.dart';
import 'package:meditation_companion/features/game/bloc/game_event.dart';
import 'package:meditation_companion/features/game/bloc/game_state.dart';
import 'package:meditation_companion/features/game/models/game_card.dart';
import 'package:meditation_companion/features/game/repository/game_repository.dart';

/// Deterministic repository returning a fixed, known deck so tests can
/// reason precisely about ids, symbols and matching outcomes.
///
/// The deck is two pairs in a stable order:
///   id 0 -> 'A'
///   id 1 -> 'A'
///   id 2 -> 'B'
///   id 3 -> 'B'
class _FakeGameRepository implements IGameRepository {
  @override
  List<GameCard> generateDeck({int pairCount = 6}) {
    return const [
      GameCard(id: 0, symbol: 'A'),
      GameCard(id: 1, symbol: 'A'),
      GameCard(id: 2, symbol: 'B'),
      GameCard(id: 3, symbol: 'B'),
    ];
  }
}

void main() {
  group('GameBloc', () {
    late _FakeGameRepository repository;

    // A tiny mismatch delay keeps flip-back behaviour deterministic and fast.
    const mismatchDelay = Duration(milliseconds: 1);

    /// The full face-down deck the fake repository hands out, used as the
    /// baseline for [GameState] in seeds.
    List<GameCard> freshDeck() => const [
          GameCard(id: 0, symbol: 'A'),
          GameCard(id: 1, symbol: 'A'),
          GameCard(id: 2, symbol: 'B'),
          GameCard(id: 3, symbol: 'B'),
        ];

    /// A state mid-game with the given [cards] override.
    GameState playingState(List<GameCard> cards) => GameState(
          cards: cards,
          status: GameStatus.playing,
        );

    setUp(() {
      repository = _FakeGameRepository();
    });

    GameBloc buildBloc() => GameBloc(
          gameRepository: repository,
          mismatchDelay: mismatchDelay,
        );

    GameCard cardOf(GameState state, int id) =>
        state.cards.firstWhere((c) => c.id == id);

    test('initial state is const GameState() with status initial and no cards',
        () {
      final bloc = buildBloc();
      addTearDown(bloc.close);

      expect(bloc.state, const GameState());
      expect(bloc.state.status, GameStatus.initial);
      expect(bloc.state.cards, isEmpty);
      expect(bloc.state.moves, 0);
      expect(bloc.state.matchedPairs, 0);
    });

    blocTest<GameBloc, GameState>(
      'GameStarted emits a playing state with the full deck and reset counters',
      build: buildBloc,
      act: (bloc) => bloc.add(const GameStarted()),
      expect: () => [
        isA<GameState>()
            .having((s) => s.status, 'status', GameStatus.playing)
            .having((s) => s.cards.length, 'cards.length', 4)
            .having((s) => s.moves, 'moves', 0)
            .having((s) => s.matchedPairs, 'matchedPairs', 0)
            .having((s) => s.totalPairs, 'totalPairs', 2),
      ],
    );

    blocTest<GameBloc, GameState>(
      'CardFlipped on a face-down card reveals it (isFlipped true)',
      build: buildBloc,
      seed: () => playingState(freshDeck()),
      act: (bloc) => bloc.add(const CardFlipped(0)),
      expect: () => [
        isA<GameState>().having(
          (s) => s.cards.firstWhere((c) => c.id == 0).isFlipped,
          'card 0 isFlipped',
          true,
        ),
      ],
      verify: (bloc) {
        expect(cardOf(bloc.state, 0).isFlipped, true);
        expect(cardOf(bloc.state, 1).isFlipped, false);
      },
    );

    blocTest<GameBloc, GameState>(
      'flipping two matching cards marks them matched and bumps counters',
      build: buildBloc,
      seed: () => playingState(freshDeck()),
      act: (bloc) {
        bloc.add(const CardFlipped(0));
        bloc.add(const CardFlipped(1));
      },
      expect: () => [
        // First reveal.
        isA<GameState>()
            .having((s) => s.cards.firstWhere((c) => c.id == 0).isFlipped,
                'card 0 isFlipped', true)
            .having((s) => s.moves, 'moves', 0),
        // Second reveal completing the matching turn.
        isA<GameState>()
            .having((s) => s.cards.firstWhere((c) => c.id == 0).isMatched,
                'card 0 isMatched', true)
            .having((s) => s.cards.firstWhere((c) => c.id == 1).isMatched,
                'card 1 isMatched', true)
            .having((s) => s.matchedPairs, 'matchedPairs', 1)
            .having((s) => s.moves, 'moves', 1)
            .having((s) => s.status, 'status', GameStatus.playing),
      ],
    );

    blocTest<GameBloc, GameState>(
      'flipping two non-matching cards bumps moves then flips them back down',
      build: buildBloc,
      seed: () => playingState(freshDeck()),
      // Allow the mismatch flip-back delay to elapse and emit.
      wait: const Duration(milliseconds: 20),
      act: (bloc) {
        bloc.add(const CardFlipped(0)); // 'A'
        bloc.add(const CardFlipped(2)); // 'B' -> mismatch
      },
      expect: () => [
        // First reveal.
        isA<GameState>().having(
            (s) => s.cards.firstWhere((c) => c.id == 0).isFlipped,
            'card 0 isFlipped',
            true),
        // Second reveal: both face up, move counted.
        isA<GameState>()
            .having((s) => s.cards.firstWhere((c) => c.id == 0).isFlipped,
                'card 0 isFlipped', true)
            .having((s) => s.cards.firstWhere((c) => c.id == 2).isFlipped,
                'card 2 isFlipped', true)
            .having((s) => s.moves, 'moves', 1),
        // After the delay: both flipped back down, move still counted.
        isA<GameState>()
            .having((s) => s.cards.firstWhere((c) => c.id == 0).isFlipped,
                'card 0 isFlipped', false)
            .having((s) => s.cards.firstWhere((c) => c.id == 2).isFlipped,
                'card 2 isFlipped', false)
            .having((s) => s.moves, 'moves', 1)
            .having((s) => s.matchedPairs, 'matchedPairs', 0),
      ],
      verify: (bloc) {
        expect(cardOf(bloc.state, 0).isFlipped, false);
        expect(cardOf(bloc.state, 2).isFlipped, false);
        expect(cardOf(bloc.state, 0).isMatched, false);
        expect(cardOf(bloc.state, 2).isMatched, false);
      },
    );

    blocTest<GameBloc, GameState>(
      'matching all pairs transitions status to won',
      build: buildBloc,
      seed: () => playingState(freshDeck()),
      act: (bloc) {
        bloc
          ..add(const CardFlipped(0)) // 'A'
          ..add(const CardFlipped(1)) // 'A' -> pair 1 matched
          ..add(const CardFlipped(2)) // 'B'
          ..add(const CardFlipped(3)); // 'B' -> pair 2 matched -> won
      },
      verify: (bloc) {
        expect(bloc.state.status, GameStatus.won);
        expect(bloc.state.matchedPairs, 2);
        expect(bloc.state.moves, 2);
        expect(bloc.state.cards.every((c) => c.isMatched), true);
      },
    );

    blocTest<GameBloc, GameState>(
      'CardFlipped is ignored when status is not playing (before GameStarted)',
      build: buildBloc,
      // No seed: state is the initial GameState (status initial).
      act: (bloc) => bloc.add(const CardFlipped(0)),
      expect: () => const <GameState>[],
    );

    blocTest<GameBloc, GameState>(
      'tapping an already-matched card is a no-op',
      build: buildBloc,
      seed: () => playingState(const [
        GameCard(id: 0, symbol: 'A', isFlipped: true, isMatched: true),
        GameCard(id: 1, symbol: 'A', isFlipped: true, isMatched: true),
        GameCard(id: 2, symbol: 'B'),
        GameCard(id: 3, symbol: 'B'),
      ]),
      act: (bloc) => bloc.add(const CardFlipped(0)),
      expect: () => const <GameState>[],
    );

    blocTest<GameBloc, GameState>(
      'tapping an already-flipped (face-up) card is a no-op',
      build: buildBloc,
      seed: () => playingState(const [
        GameCard(id: 0, symbol: 'A', isFlipped: true),
        GameCard(id: 1, symbol: 'A'),
        GameCard(id: 2, symbol: 'B'),
        GameCard(id: 3, symbol: 'B'),
      ]),
      act: (bloc) => bloc.add(const CardFlipped(0)),
      expect: () => const <GameState>[],
    );
  });
}
