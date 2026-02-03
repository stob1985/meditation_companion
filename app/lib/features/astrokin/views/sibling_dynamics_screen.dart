import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/astrokin_bloc.dart';
import '../bloc/astrokin_event.dart';
import '../bloc/astrokin_state.dart';
import '../models/models.dart';
import '../theme/astrokin_theme.dart';

class SiblingDynamicsScreen extends StatefulWidget {
  const SiblingDynamicsScreen({super.key});

  @override
  State<SiblingDynamicsScreen> createState() => _SiblingDynamicsScreenState();
}

class _SiblingDynamicsScreenState extends State<SiblingDynamicsScreen> {
  @override
  void initState() {
    super.initState();
    context.read<AstroKinBloc>().add(LoadSiblingDynamics());
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AstroKinBloc, AstroKinState>(
      builder: (context, state) {
        if (!state.hasMultipleChildren) {
          return _buildNotEnoughChildrenView(context);
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(AstroKinSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Overview Card
              _buildOverviewCard(context, state),

              const SizedBox(height: AstroKinSpacing.lg),

              // Sibling Pairs
              Text(
                'Sibling Relationships',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: AstroKinSpacing.md),

              if (state.siblingDynamics.isEmpty)
                const Center(child: CircularProgressIndicator())
              else
                ...state.siblingDynamics.map((dynamic) => Padding(
                      padding: const EdgeInsets.only(bottom: AstroKinSpacing.md),
                      child: _buildDynamicCard(context, dynamic),
                    )),
            ],
          ),
        );
      },
    );
  }

  Widget _buildNotEnoughChildrenView(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.people_outline,
              size: 80,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: AstroKinSpacing.lg),
            Text(
              'Add More Children',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: AstroKinSpacing.sm),
            Text(
              'Add at least two children to your family profile to see sibling dynamics and relationship insights.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AstroKinTheme.textSecondary,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.lg),
            ElevatedButton.icon(
              onPressed: () {
                // Navigate to family profile
              },
              icon: const Icon(Icons.add),
              label: const Text('Add Child'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewCard(BuildContext context, AstroKinState state) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.family_restroom,
                  color: AstroKinTheme.primaryBlue,
                ),
                const SizedBox(width: AstroKinSpacing.sm),
                Text(
                  'Sibling Overview',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: AstroKinSpacing.md),
            Text(
              'Understanding your children\'s astrological compatibility can help you navigate their relationships better.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AstroKinTheme.textSecondary,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.md),
            Wrap(
              spacing: AstroKinSpacing.sm,
              runSpacing: AstroKinSpacing.sm,
              children: state.children.map((child) {
                return Chip(
                  avatar: Text(child.zodiacSign.symbol),
                  label: Text(child.name),
                  backgroundColor: AstroKinTheme.getZodiacColor(child.zodiacSign.element.name)
                      .withValues(alpha: 0.1),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDynamicCard(BuildContext context, SiblingDynamic dynamic) {
    return Card(
      child: InkWell(
        onTap: () => _showDetailedAnalysis(context, dynamic),
        borderRadius: BorderRadius.circular(AstroKinRadius.lg),
        child: Padding(
          padding: const EdgeInsets.all(AstroKinSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Sibling Pair Header
              Row(
                children: [
                  _buildSiblingAvatar(context, dynamic.sibling1),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: AstroKinSpacing.sm),
                    child: Column(
                      children: [
                        Text(
                          dynamic.dynamicEmoji,
                          style: const TextStyle(fontSize: 24),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: AstroKinSpacing.sm,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: _getDynamicColor(dynamic.overallDynamic).withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(AstroKinRadius.sm),
                          ),
                          child: Text(
                            dynamic.dynamicDisplayName,
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: _getDynamicColor(dynamic.overallDynamic),
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  _buildSiblingAvatar(context, dynamic.sibling2),
                  const Spacer(),
                  _buildCompatibilityScore(context, dynamic.compatibilityScore),
                ],
              ),

              const SizedBox(height: AstroKinSpacing.md),

              // Names
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    dynamic.sibling1.name,
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  Text(
                    ' & ',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: AstroKinTheme.textSecondary,
                        ),
                  ),
                  Text(
                    dynamic.sibling2.name,
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                ],
              ),

              const Divider(height: AstroKinSpacing.lg),

              // Strengths Preview
              if (dynamic.strengths.isNotEmpty) ...[
                Row(
                  children: [
                    Icon(
                      Icons.favorite,
                      size: 16,
                      color: AstroKinTheme.energyHigh,
                    ),
                    const SizedBox(width: AstroKinSpacing.xs),
                    Text(
                      'Strength: ',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    Expanded(
                      child: Text(
                        dynamic.strengths.first,
                        style: Theme.of(context).textTheme.bodySmall,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ],

              const SizedBox(height: AstroKinSpacing.sm),

              // Tip Preview
              if (dynamic.tips.isNotEmpty) ...[
                Row(
                  children: [
                    Icon(
                      Icons.lightbulb_outline,
                      size: 16,
                      color: AstroKinTheme.accentGold,
                    ),
                    const SizedBox(width: AstroKinSpacing.xs),
                    Text(
                      'Tip: ',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    Expanded(
                      child: Text(
                        dynamic.tips.first,
                        style: Theme.of(context).textTheme.bodySmall,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ],

              const SizedBox(height: AstroKinSpacing.sm),
              Center(
                child: Text(
                  'Tap for detailed analysis',
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

  Widget _buildSiblingAvatar(BuildContext context, FamilyMember member) {
    final color = AstroKinTheme.getZodiacColor(member.zodiacSign.element.name);
    return Container(
      width: 50,
      height: 50,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color, color.withValues(alpha: 0.5)],
        ),
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Text(
          member.zodiacSign.symbol,
          style: const TextStyle(fontSize: 24, color: Colors.white),
        ),
      ),
    );
  }

  Widget _buildCompatibilityScore(BuildContext context, double score) {
    final percentage = (score * 100).round();
    return Column(
      children: [
        Text(
          '$percentage%',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: _getScoreColor(score),
              ),
        ),
        Text(
          'Compatibility',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  Color _getDynamicColor(DynamicType type) {
    switch (type) {
      case DynamicType.harmonious:
        return AstroKinTheme.energyHigh;
      case DynamicType.complementary:
        return AstroKinTheme.primaryBlue;
      case DynamicType.neutral:
        return AstroKinTheme.energyMedium;
      case DynamicType.challenging:
        return AstroKinTheme.energyLow;
    }
  }

  Color _getScoreColor(double score) {
    if (score > 0.7) return AstroKinTheme.energyHigh;
    if (score > 0.4) return AstroKinTheme.energyMedium;
    return AstroKinTheme.energyLow;
  }

  void _showDetailedAnalysis(BuildContext context, SiblingDynamic dynamic) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _DetailedAnalysisSheet(dynamic: dynamic),
    );
  }
}

class _DetailedAnalysisSheet extends StatelessWidget {
  final SiblingDynamic dynamic;

  const _DetailedAnalysisSheet({required this.dynamic});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
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

          // Content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(AstroKinSpacing.lg),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Center(
                    child: Column(
                      children: [
                        Text(
                          '${dynamic.sibling1.name} & ${dynamic.sibling2.name}',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        const SizedBox(height: AstroKinSpacing.xs),
                        Text(
                          '${dynamic.sibling1.zodiacSign.name} ${dynamic.sibling1.zodiacSign.symbol} '
                          '+ ${dynamic.sibling2.zodiacSign.name} ${dynamic.sibling2.zodiacSign.symbol}',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: AstroKinTheme.textSecondary,
                              ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: AstroKinSpacing.lg),

                  // Compatibility Meter
                  _buildCompatibilityMeter(context),

                  const SizedBox(height: AstroKinSpacing.lg),

                  // Aspect Scores
                  _buildAspectScores(context),

                  const SizedBox(height: AstroKinSpacing.lg),

                  // Strengths
                  _buildSection(
                    context,
                    title: 'Strengths',
                    icon: Icons.favorite,
                    iconColor: AstroKinTheme.energyHigh,
                    items: dynamic.strengths,
                  ),

                  const SizedBox(height: AstroKinSpacing.lg),

                  // Challenges
                  _buildSection(
                    context,
                    title: 'Challenges',
                    icon: Icons.warning_amber_outlined,
                    iconColor: AstroKinTheme.energyLow,
                    items: dynamic.challenges,
                  ),

                  const SizedBox(height: AstroKinSpacing.lg),

                  // Tips
                  _buildSection(
                    context,
                    title: 'Tips for Parents',
                    icon: Icons.lightbulb_outline,
                    iconColor: AstroKinTheme.accentGold,
                    items: dynamic.tips,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCompatibilityMeter(BuildContext context) {
    final percentage = (dynamic.compatibilityScore * 100).round();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Overall Compatibility',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Text(
                  '$percentage%',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: _getScoreColor(dynamic.compatibilityScore),
                      ),
                ),
              ],
            ),
            const SizedBox(height: AstroKinSpacing.sm),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: dynamic.compatibilityScore,
                backgroundColor: Colors.grey.shade200,
                valueColor: AlwaysStoppedAnimation(_getScoreColor(dynamic.compatibilityScore)),
                minHeight: 10,
              ),
            ),
            const SizedBox(height: AstroKinSpacing.sm),
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AstroKinSpacing.md,
                vertical: AstroKinSpacing.sm,
              ),
              decoration: BoxDecoration(
                color: _getDynamicColor(dynamic.overallDynamic).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(AstroKinRadius.md),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    dynamic.dynamicEmoji,
                    style: const TextStyle(fontSize: 20),
                  ),
                  const SizedBox(width: AstroKinSpacing.sm),
                  Text(
                    '${dynamic.dynamicDisplayName} Relationship',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: _getDynamicColor(dynamic.overallDynamic),
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAspectScores(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Relationship Aspects',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.md),
            ...dynamic.aspectScores.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.only(bottom: AstroKinSpacing.sm),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          _getAspectLabel(entry.key),
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                        Text(
                          '${(entry.value * 100).round()}%',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(2),
                      child: LinearProgressIndicator(
                        value: entry.value,
                        backgroundColor: Colors.grey.shade200,
                        valueColor: AlwaysStoppedAnimation(_getScoreColor(entry.value)),
                        minHeight: 6,
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Color iconColor,
    required List<String> items,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: iconColor, size: 20),
            const SizedBox(width: AstroKinSpacing.sm),
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ],
        ),
        const SizedBox(height: AstroKinSpacing.sm),
        ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: AstroKinSpacing.sm),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    margin: const EdgeInsets.only(top: 6),
                    width: 6,
                    height: 6,
                    decoration: BoxDecoration(
                      color: iconColor,
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
    );
  }

  String _getAspectLabel(RelationshipAspect aspect) {
    switch (aspect) {
      case RelationshipAspect.communication:
        return 'Communication';
      case RelationshipAspect.playStyle:
        return 'Play Style';
      case RelationshipAspect.conflictResolution:
        return 'Conflict Resolution';
      case RelationshipAspect.sharedInterests:
        return 'Shared Interests';
      case RelationshipAspect.emotionalConnection:
        return 'Emotional Connection';
    }
  }

  Color _getDynamicColor(DynamicType type) {
    switch (type) {
      case DynamicType.harmonious:
        return AstroKinTheme.energyHigh;
      case DynamicType.complementary:
        return AstroKinTheme.primaryBlue;
      case DynamicType.neutral:
        return AstroKinTheme.energyMedium;
      case DynamicType.challenging:
        return AstroKinTheme.energyLow;
    }
  }

  Color _getScoreColor(double score) {
    if (score > 0.7) return AstroKinTheme.energyHigh;
    if (score > 0.4) return AstroKinTheme.energyMedium;
    return AstroKinTheme.energyLow;
  }
}
