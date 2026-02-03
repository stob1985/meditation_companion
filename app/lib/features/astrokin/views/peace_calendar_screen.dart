import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/astrokin_bloc.dart';
import '../bloc/astrokin_event.dart';
import '../bloc/astrokin_state.dart';
import '../models/models.dart';
import '../widgets/widgets.dart';
import '../theme/astrokin_theme.dart';

class PeaceCalendarScreen extends StatefulWidget {
  const PeaceCalendarScreen({super.key});

  @override
  State<PeaceCalendarScreen> createState() => _PeaceCalendarScreenState();
}

class _PeaceCalendarScreenState extends State<PeaceCalendarScreen> {
  late DateTime _focusedMonth;
  DateTime? _selectedDay;

  @override
  void initState() {
    super.initState();
    _focusedMonth = DateTime.now();
    _selectedDay = DateTime.now();
    _loadEnergyHistory();
  }

  void _loadEnergyHistory() {
    final start = DateTime(_focusedMonth.year, _focusedMonth.month, 1);
    final end = DateTime(_focusedMonth.year, _focusedMonth.month + 1, 0);
    context.read<AstroKinBloc>().add(LoadEnergyHistory(
          startDate: start,
          endDate: end,
        ));
    context.read<AstroKinBloc>().add(const LoadUpcomingEvents(days: 60));
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AstroKinBloc, AstroKinState>(
      builder: (context, state) {
        return Column(
          children: [
            // Calendar Header
            _buildCalendarHeader(context),

            // Calendar Grid
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(AstroKinSpacing.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Simple Calendar
                    _buildCalendar(context, state),

                    const SizedBox(height: AstroKinSpacing.lg),

                    // Selected Day Info
                    if (_selectedDay != null) _buildSelectedDayInfo(context, state),

                    const SizedBox(height: AstroKinSpacing.lg),

                    // Upcoming Events
                    _buildUpcomingEvents(context, state),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildCalendarHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AstroKinSpacing.md,
        vertical: AstroKinSpacing.sm,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: const Icon(Icons.chevron_left),
            onPressed: () {
              setState(() {
                _focusedMonth = DateTime(_focusedMonth.year, _focusedMonth.month - 1);
              });
              _loadEnergyHistory();
            },
          ),
          Text(
            _formatMonth(_focusedMonth),
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          IconButton(
            icon: const Icon(Icons.chevron_right),
            onPressed: () {
              setState(() {
                _focusedMonth = DateTime(_focusedMonth.year, _focusedMonth.month + 1);
              });
              _loadEnergyHistory();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildCalendar(BuildContext context, AstroKinState state) {
    final daysInMonth = DateTime(_focusedMonth.year, _focusedMonth.month + 1, 0).day;
    final firstDayOfMonth = DateTime(_focusedMonth.year, _focusedMonth.month, 1);
    final startingWeekday = firstDayOfMonth.weekday;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Column(
          children: [
            // Weekday headers
            Row(
              children: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                  .map((day) => Expanded(
                        child: Center(
                          child: Text(
                            day,
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: AstroKinTheme.textSecondary,
                                ),
                          ),
                        ),
                      ))
                  .toList(),
            ),
            const SizedBox(height: AstroKinSpacing.sm),
            // Calendar days
            ...List.generate(6, (weekIndex) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  children: List.generate(7, (dayIndex) {
                    final dayNumber = weekIndex * 7 + dayIndex - startingWeekday + 2;
                    if (dayNumber < 1 || dayNumber > daysInMonth) {
                      return const Expanded(child: SizedBox(height: 44));
                    }

                    final date = DateTime(_focusedMonth.year, _focusedMonth.month, dayNumber);
                    final energy = _getEnergyForDate(state.energyHistory, date);
                    final hasEvent = _hasEventOnDate(state.upcomingEvents, date);
                    final isSelected = _isSameDay(_selectedDay, date);
                    final isToday = _isSameDay(DateTime.now(), date);

                    return Expanded(
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedDay = date;
                          });
                          context.read<AstroKinBloc>().add(LoadEventsForDate(date));
                          context.read<AstroKinBloc>().add(LoadFamilyEnergy(date: date));
                        },
                        child: Container(
                          height: 44,
                          margin: const EdgeInsets.all(2),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? AstroKinTheme.primaryBlue
                                : energy != null
                                    ? _getEnergyColor(energy.overallType).withValues(alpha: 0.2)
                                    : null,
                            borderRadius: BorderRadius.circular(AstroKinRadius.sm),
                            border: isToday
                                ? Border.all(color: AstroKinTheme.primaryBlue, width: 2)
                                : null,
                          ),
                          child: Stack(
                            alignment: Alignment.center,
                            children: [
                              Text(
                                dayNumber.toString(),
                                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                      color: isSelected ? Colors.white : null,
                                      fontWeight: isToday ? FontWeight.bold : null,
                                    ),
                              ),
                              if (hasEvent)
                                Positioned(
                                  bottom: 4,
                                  child: Container(
                                    width: 6,
                                    height: 6,
                                    decoration: BoxDecoration(
                                      color: isSelected ? Colors.white : AstroKinTheme.primaryPurple,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }),
                ),
              );
            }),
            // Legend
            const SizedBox(height: AstroKinSpacing.md),
            _buildLegend(context),
          ],
        ),
      ),
    );
  }

  Widget _buildLegend(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _buildLegendItem(context, AstroKinTheme.energyHigh, 'High Energy'),
        const SizedBox(width: AstroKinSpacing.md),
        _buildLegendItem(context, AstroKinTheme.energyMedium, 'Medium'),
        const SizedBox(width: AstroKinSpacing.md),
        _buildLegendItem(context, AstroKinTheme.energyLow, 'Low Energy'),
      ],
    );
  }

  Widget _buildLegendItem(BuildContext context, Color color, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  Widget _buildSelectedDayInfo(BuildContext context, AstroKinState state) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.calendar_today,
                  size: 20,
                  color: AstroKinTheme.primaryBlue,
                ),
                const SizedBox(width: AstroKinSpacing.sm),
                Text(
                  _formatFullDate(_selectedDay!),
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: AstroKinSpacing.md),
            if (state.currentEnergy != null) ...[
              Row(
                children: [
                  EnergyGauge(
                    energy: state.currentEnergy,
                    size: 80,
                  ),
                  const SizedBox(width: AstroKinSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Family Energy',
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                        const SizedBox(height: AstroKinSpacing.xs),
                        ...state.currentEnergy!.insights.take(2).map((insight) => Text(
                              insight,
                              style: Theme.of(context).textTheme.bodySmall,
                            )),
                      ],
                    ),
                  ),
                ],
              ),
            ],
            if (state.todayEvents.isNotEmpty) ...[
              const Divider(height: AstroKinSpacing.lg),
              Text(
                'Events on this day',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: AstroKinSpacing.sm),
              ...state.todayEvents.map((event) => Padding(
                    padding: const EdgeInsets.only(bottom: AstroKinSpacing.sm),
                    child: CompactEventCard(event: event),
                  )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildUpcomingEvents(BuildContext context, AstroKinState state) {
    final upcomingEvents = state.upcomingEvents;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Upcoming Events',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: AstroKinSpacing.md),
        if (upcomingEvents.isEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(AstroKinSpacing.lg),
              child: Center(
                child: Text(
                  'No upcoming events',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AstroKinTheme.textSecondary,
                      ),
                ),
              ),
            ),
          )
        else
          ...upcomingEvents.map((event) => Padding(
                padding: const EdgeInsets.only(bottom: AstroKinSpacing.sm),
                child: EventCard(event: event),
              )),
      ],
    );
  }

  FamilyEnergySnapshot? _getEnergyForDate(
      List<FamilyEnergySnapshot> history, DateTime date) {
    try {
      return history.firstWhere((e) => _isSameDay(e.date, date));
    } catch (_) {
      return null;
    }
  }

  bool _hasEventOnDate(List<AstrologicalEvent> events, DateTime date) {
    return events.any((e) => e.isActiveOn(date));
  }

  bool _isSameDay(DateTime? a, DateTime? b) {
    if (a == null || b == null) return false;
    return a.year == b.year && a.month == b.month && a.day == b.day;
  }

  Color _getEnergyColor(EnergyType type) {
    switch (type) {
      case EnergyType.high:
        return AstroKinTheme.energyHigh;
      case EnergyType.medium:
        return AstroKinTheme.energyMedium;
      case EnergyType.low:
        return AstroKinTheme.energyLow;
    }
  }

  String _formatMonth(DateTime date) {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return '${months[date.month - 1]} ${date.year}';
  }

  String _formatFullDate(DateTime date) {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    const weekdays = [
      'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ];
    return '${weekdays[date.weekday - 1]}, ${months[date.month - 1]} ${date.day}';
  }
}
