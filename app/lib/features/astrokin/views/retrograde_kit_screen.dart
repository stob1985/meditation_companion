import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/astrokin_bloc.dart';
import '../bloc/astrokin_event.dart';
import '../bloc/astrokin_state.dart';
import '../models/models.dart';
import '../widgets/widgets.dart';
import '../theme/astrokin_theme.dart';

class RetrogradeKitScreen extends StatefulWidget {
  const RetrogradeKitScreen({super.key});

  @override
  State<RetrogradeKitScreen> createState() => _RetrogradeKitScreenState();
}

class _RetrogradeKitScreenState extends State<RetrogradeKitScreen> {
  @override
  void initState() {
    super.initState();
    context.read<AstroKinBloc>().add(LoadActiveRetrogrades());
    context.read<AstroKinBloc>().add(const LoadUpcomingRetrogrades());
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AstroKinBloc, AstroKinState>(
      builder: (context, state) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(AstroKinSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              _buildHeader(context),

              const SizedBox(height: AstroKinSpacing.lg),

              // Active Retrogrades
              if (state.activeRetrogrades.isNotEmpty) ...[
                Text(
                  'Active Retrogrades',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: AstroKinSpacing.md),
                ...state.activeRetrogrades.map((retro) => Padding(
                      padding: const EdgeInsets.only(bottom: AstroKinSpacing.md),
                      child: _buildActiveRetrogradeCard(context, retro),
                    )),
                const SizedBox(height: AstroKinSpacing.lg),
              ],

              // No Active Retrogrades
              if (state.activeRetrogrades.isEmpty) ...[
                _buildNoActiveRetrogrades(context),
                const SizedBox(height: AstroKinSpacing.lg),
              ],

              // Upcoming Retrogrades
              Text(
                'Upcoming Retrogrades',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: AstroKinSpacing.md),
              if (state.upcomingRetrogrades.isEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(AstroKinSpacing.lg),
                    child: Center(
                      child: Text(
                        'No retrogrades in the next 90 days',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: AstroKinTheme.textSecondary,
                            ),
                      ),
                    ),
                  ),
                )
              else
                ...state.upcomingRetrogrades.map((retro) => Padding(
                      padding: const EdgeInsets.only(bottom: AstroKinSpacing.md),
                      child: RetrogradeProgressCard(
                        retrograde: retro,
                        onTap: () => _showRetrogradeDetails(context, retro),
                      ),
                    )),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AstroKinSpacing.lg),
      decoration: BoxDecoration(
        gradient: AstroKinTheme.nightGradient,
        borderRadius: BorderRadius.circular(AstroKinRadius.lg),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(AstroKinSpacing.md),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(AstroKinRadius.md),
                ),
                child: const Icon(
                  Icons.shield_outlined,
                  color: Colors.white,
                  size: 32,
                ),
              ),
              const SizedBox(width: AstroKinSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Retrograde Survival Kit',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    Text(
                      'Navigate challenging cosmic periods with ease',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.white.withValues(alpha: 0.8),
                          ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: AstroKinSpacing.md),
          Text(
            'Retrogrades are periods when planets appear to move backward. '
            'While they can bring challenges, they also offer opportunities for '
            'reflection and growth.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.white.withValues(alpha: 0.9),
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildNoActiveRetrogrades(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.xl),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(AstroKinSpacing.lg),
              decoration: BoxDecoration(
                color: AstroKinTheme.energyHigh.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.check_circle_outline,
                size: 48,
                color: AstroKinTheme.energyHigh,
              ),
            ),
            const SizedBox(height: AstroKinSpacing.md),
            Text(
              'All Clear!',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.sm),
            Text(
              'No major retrogrades are currently active. This is a good time for new beginnings and forward momentum.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AstroKinTheme.textSecondary,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActiveRetrogradeCard(BuildContext context, RetrogradeInfo retro) {
    return Card(
      color: AstroKinTheme.primaryPurple.withValues(alpha: 0.05),
      child: InkWell(
        onTap: () => _showRetrogradeDetails(context, retro),
        borderRadius: BorderRadius.circular(AstroKinRadius.lg),
        child: Padding(
          padding: const EdgeInsets.all(AstroKinSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Text(
                    retro.planetSymbol,
                    style: const TextStyle(fontSize: 40),
                  ),
                  const SizedBox(width: AstroKinSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              '${retro.planetName} Retrograde',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            const SizedBox(width: AstroKinSpacing.sm),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: AstroKinSpacing.sm,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: AstroKinTheme.energyLow.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(AstroKinRadius.sm),
                              ),
                              child: Text(
                                'ACTIVE',
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: AstroKinTheme.energyLow,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 10,
                                    ),
                              ),
                            ),
                          ],
                        ),
                        Text(
                          retro.affectedArea,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AstroKinTheme.textSecondary,
                              ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: AstroKinSpacing.md),

              // Progress
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '${(retro.progress * 100).round()}% Complete',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      Text(
                        '${retro.daysRemaining} days remaining',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: AstroKinTheme.primaryPurple,
                            ),
                      ),
                    ],
                  ),
                  const SizedBox(height: AstroKinSpacing.xs),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: retro.progress,
                      backgroundColor: Colors.grey.shade200,
                      valueColor: const AlwaysStoppedAnimation(AstroKinTheme.primaryPurple),
                      minHeight: 8,
                    ),
                  ),
                ],
              ),

              const Divider(height: AstroKinSpacing.lg),

              // Quick Tips
              Row(
                children: [
                  Expanded(
                    child: _buildQuickTip(
                      context,
                      icon: Icons.check_circle_outline,
                      iconColor: AstroKinTheme.energyHigh,
                      title: 'Do',
                      text: retro.doList.isNotEmpty ? retro.doList.first : 'Stay patient',
                    ),
                  ),
                  const SizedBox(width: AstroKinSpacing.md),
                  Expanded(
                    child: _buildQuickTip(
                      context,
                      icon: Icons.cancel_outlined,
                      iconColor: AstroKinTheme.energyLow,
                      title: "Don't",
                      text: retro.dontList.isNotEmpty ? retro.dontList.first : 'Rush decisions',
                    ),
                  ),
                ],
              ),

              const SizedBox(height: AstroKinSpacing.sm),
              Center(
                child: Text(
                  'Tap for complete survival guide',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AstroKinTheme.primaryBlue,
                      ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickTip(
    BuildContext context, {
    required IconData icon,
    required Color iconColor,
    required String title,
    required String text,
  }) {
    return Container(
      padding: const EdgeInsets.all(AstroKinSpacing.sm),
      decoration: BoxDecoration(
        color: iconColor.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(AstroKinRadius.sm),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: iconColor),
              const SizedBox(width: 4),
              Text(
                title,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: iconColor,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            text,
            style: Theme.of(context).textTheme.bodySmall,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  void _showRetrogradeDetails(BuildContext context, RetrogradeInfo retro) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _RetrogradeDetailsSheet(retrograde: retro),
    );
  }
}

class _RetrogradeDetailsSheet extends StatelessWidget {
  final RetrogradeInfo retrograde;

  const _RetrogradeDetailsSheet({required this.retrograde});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.9,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(AstroKinRadius.xl)),
      ),
      child: Column(
        children: [
          // Handle
          Container(
            margin: const EdgeInsets.only(top: AstroKinSpacing.sm),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey.shade300,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // Header
          Container(
            padding: const EdgeInsets.all(AstroKinSpacing.lg),
            decoration: BoxDecoration(
              gradient: AstroKinTheme.nightGradient,
            ),
            child: Row(
              children: [
                Text(
                  retrograde.planetSymbol,
                  style: const TextStyle(fontSize: 48, color: Colors.white),
                ),
                const SizedBox(width: AstroKinSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${retrograde.planetName} Retrograde',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      Text(
                        retrograde.affectedArea,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Colors.white.withValues(alpha: 0.8),
                            ),
                      ),
                      const SizedBox(height: AstroKinSpacing.xs),
                      Text(
                        '${_formatDate(retrograde.startDate)} - ${_formatDate(retrograde.endDate)}',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.white.withValues(alpha: 0.7),
                            ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(AstroKinSpacing.lg),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Description
                  Text(
                    retrograde.description,
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),

                  const SizedBox(height: AstroKinSpacing.xl),

                  // Do's
                  _buildListSection(
                    context,
                    title: 'What TO DO',
                    icon: Icons.check_circle,
                    iconColor: AstroKinTheme.energyHigh,
                    items: retrograde.doList,
                  ),

                  const SizedBox(height: AstroKinSpacing.lg),

                  // Don'ts
                  _buildListSection(
                    context,
                    title: 'What to AVOID',
                    icon: Icons.cancel,
                    iconColor: AstroKinTheme.energyLow,
                    items: retrograde.dontList,
                  ),

                  const SizedBox(height: AstroKinSpacing.lg),

                  // Family Tips
                  _buildListSection(
                    context,
                    title: 'Family Tips',
                    icon: Icons.family_restroom,
                    iconColor: AstroKinTheme.primaryBlue,
                    items: retrograde.familyTips,
                  ),

                  const SizedBox(height: AstroKinSpacing.lg),

                  // Communication Tips
                  _buildListSection(
                    context,
                    title: 'Communication Tips',
                    icon: Icons.chat_bubble_outline,
                    iconColor: AstroKinTheme.primaryPurple,
                    items: retrograde.communicationTips,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildListSection(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Color iconColor,
    required List<String> items,
  }) {
    if (items.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: iconColor),
                const SizedBox(width: AstroKinSpacing.sm),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: AstroKinSpacing.md),
            ...items.map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: AstroKinSpacing.sm),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        margin: const EdgeInsets.only(top: 6),
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: iconColor.withValues(alpha: 0.5),
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: AstroKinSpacing.sm),
                      Expanded(
                        child: Text(
                          item,
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[date.month - 1]} ${date.day}';
  }
}
