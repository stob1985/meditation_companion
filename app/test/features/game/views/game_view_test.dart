import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:meditation_companion/features/game/bloc/game_bloc.dart';
import 'package:meditation_companion/features/game/bloc/game_event.dart';
import 'package:meditation_companion/features/game/models/game_card.dart';
import 'package:meditation_companion/features/game/repository/game_repository.dart';
import 'package:meditation_companion/features/game/views/game_view.dart';

/// Deterministic repository that always returns the same small deck:
/// symbols ['A', 'A', 'B', 'B'] with ids 0..3.
///
/// Card 0 and 1 form a matching pair ('A'); card 2 and 3 form the other
/// matching pair ('B'). The layout never changes, so tests can rely on a
/// known ordering when tapping cards by id.
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
  group('GameView', () {
    late GameBloc bloc;

    setUp(() {
      bloc = GameBloc(
        gameRepository: _FakeGameRepository(),
        // Keep the mismatch reveal short for fast, deterministic settling.
        mismatchDelay: const Duration(milliseconds: 10),
      );
    });

    tearDown(() {
      bloc.close();
    });

    Widget buildSubject() {
      return MaterialApp(
        home: BlocProvider<GameBloc>.value(
          value: bloc,
          child: const GameView(),
        ),
      );
    }

    // Bloc events are processed on the real event loop, which the fake-async
    // test clock does not advance via pump() alone. runAsync lets the bloc
    // handle the queued event and emit, then pump() renders the new state and
    // settles the tile AnimatedContainers.
    Future<void> process(WidgetTester tester) async {
      await tester
          .runAsync(() => Future<void>.delayed(const Duration(milliseconds: 30)));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 250));
    }

    /// Starts the game (status -> playing) and lets the UI settle.
    Future<void> startGame(WidgetTester tester) async {
      await tester.pumpWidget(buildSubject());
      bloc.add(const GameStarted(pairCount: 2));
      await process(tester);
    }

    /// Taps the card with [id] and settles the resulting animations.
    Future<void> tapCard(WidgetTester tester, int id) async {
      await tester.tap(find.byKey(ValueKey('card_$id')));
      await process(tester);
    }

    testWidgets('shows a progress indicator before a game starts',
        (tester) async {
      await tester.pumpWidget(buildSubject());
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('renders the status bar with Moves and Pairs after start',
        (tester) async {
      await startGame(tester);

      expect(find.text('Moves: 0'), findsOneWidget);
      expect(find.text('Pairs: 0/2'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets('renders one tile per card', (tester) async {
      await startGame(tester);

      expect(find.byKey(const ValueKey('card_0')), findsOneWidget);
      expect(find.byKey(const ValueKey('card_1')), findsOneWidget);
      expect(find.byKey(const ValueKey('card_2')), findsOneWidget);
      expect(find.byKey(const ValueKey('card_3')), findsOneWidget);
    });

    testWidgets('tapping a face-down card reveals its symbol', (tester) async {
      await startGame(tester);

      // Symbols are hidden while face down.
      expect(find.text('A'), findsNothing);

      await tapCard(tester, 0);

      // Card 0 carries symbol 'A' and should now be visible.
      expect(find.text('A'), findsOneWidget);
    });

    testWidgets('AppBar has a refresh action that resets the game',
        (tester) async {
      await startGame(tester);

      final refreshFinder = find.widgetWithIcon(IconButton, Icons.refresh);
      expect(refreshFinder, findsOneWidget);

      // Reveal one card, then reset; the symbol should be hidden again.
      await tapCard(tester, 0);
      expect(find.text('A'), findsOneWidget);

      await tester.tap(refreshFinder);
      await process(tester);

      expect(find.text('A'), findsNothing);
      expect(find.text('Moves: 0'), findsOneWidget);
      expect(find.text('Pairs: 0/2'), findsOneWidget);
    });

    testWidgets('shows the win banner and Play again button when won',
        (tester) async {
      await startGame(tester);

      // Match the first pair (A: ids 0 & 1).
      await tapCard(tester, 0);
      await tapCard(tester, 1);

      // Match the second pair (B: ids 2 & 3) -> game won.
      await tapCard(tester, 2);
      await tapCard(tester, 3);

      expect(find.text('🎉 You won in 2 moves!'), findsOneWidget);
      expect(find.widgetWithText(ElevatedButton, 'Play again'), findsOneWidget);
    });
  });
}
