import { Component, OnInit, computed, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';

interface DealInfo {
  client_company: string;
  client_contact_name: string;
  client_email: string;
  client_phone: string;
  client_ico: string;
}

interface QuestionnaireForm {
  [key: string]: unknown;
  // Section A
  a_company_name: string;
  a_ico: string;
  a_contact_person: string;
  a_email: string;
  a_phone: string;
  a_industry: string;
  a_industry_other: string;
  a_employee_count: string;
  a_annual_revenue: string;
  a_current_it: string[];
  a_it_satisfaction: string;
  // Section B
  b_main_categories: string[];
  b_primary_goal: string;
  b_target_users: string[];
  b_estimated_users: string;
  // Section C
  c_platform: string[];
  c_offline_mode: string;
  c_user_roles: string[];
  c_auth_methods: string[];
  c_has_payments: string;
  c_payment_gateway: string[];
  c_multilingual: string;
  c_has_design: string;
  c_key_features: string;
  c_existing_codebase: string;
  c_repo_access: string;
  // Section D
  d_website_type: string;
  d_product_count: string;
  d_erp_connection: string;
  d_erp_system: string;
  d_has_domain: string;
  d_has_hosting: string;
  d_seo_requirements: string;
  d_content_management: string;
  d_preferred_cms: string;
  // Section E
  e_ai_solution_type: string[];
  e_data_sources: string[];
  e_data_volume: string;
  e_local_ai_requirement: string;
  e_gdpr_sensitivity: string;
  e_existing_automation: string;
  e_ai_language: string[];
  // Section F
  f_system_type: string[];
  f_current_system: string;
  f_dissatisfaction_reasons: string[];
  f_custom_vs_ready: string;
  f_concurrent_users: string;
  f_data_migration: string;
  // Section G
  g_systems_to_connect: string[];
  g_systems_details: string;
  g_integration_direction: string;
  g_sync_frequency: string;
  g_has_api_docs: string;
  // Section H
  h_security_service_type: string[];
  h_had_incident: string;
  h_regulatory_requirements: string[];
  // Section I
  i_data_needs: string[];
  i_data_sources: string[];
  i_existing_bi_tool: string;
  i_report_users: string[];
  // Section J
  j_support_type: string[];
  j_required_sla: string;
  j_training_type: string[];
  j_training_count: string;
  j_training_format: string;
  // Section K
  k_budget_range: string;
  k_pricing_model: string;
  k_launch_deadline: string;
  k_specific_deadline: string;
  k_prefers_mvp: string;
  k_priority: string;
  k_decision_maker: string;
  k_decision_horizon: string;
  // Section L
  l_has_it_team: string;
  l_preferred_stack: string[];
  l_hosting_preference: string;
  l_database_preference: string;
  l_cicd_devops: string;
  l_code_ownership: string;
  // Section M
  m_lead_source: string;
  m_next_step: string;
  m_next_contact_date: string;
  m_sales_notes: string;
  m_lead_rating: string;
}

type StepDef = { id: string; label: string; conditional?: boolean };

@Component({
  selector: 'app-questionnaire-form',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './questionnaire-form.component.html',
  styleUrl: './questionnaire-form.component.scss',
})
export class QuestionnaireFormComponent implements OnInit {
  dealId = 0;
  dealInfo = signal<string>('');
  currentStep = signal(0);
  submitting = signal(false);
  aiLoading = signal(false);
  aiText = signal('');
  aiHighlighted = signal<Set<string>>(new Set());

  form: QuestionnaireForm = {
    a_company_name: '',
    a_ico: '',
    a_contact_person: '',
    a_email: '',
    a_phone: '',
    a_industry: '',
    a_industry_other: '',
    a_employee_count: '',
    a_annual_revenue: '',
    a_current_it: [],
    a_it_satisfaction: '',
    b_main_categories: [],
    b_primary_goal: '',
    b_target_users: [],
    b_estimated_users: '',
    c_platform: [],
    c_offline_mode: '',
    c_user_roles: [],
    c_auth_methods: [],
    c_has_payments: '',
    c_payment_gateway: [],
    c_multilingual: '',
    c_has_design: '',
    c_key_features: '',
    c_existing_codebase: '',
    c_repo_access: '',
    d_website_type: '',
    d_product_count: '',
    d_erp_connection: '',
    d_erp_system: '',
    d_has_domain: '',
    d_has_hosting: '',
    d_seo_requirements: '',
    d_content_management: '',
    d_preferred_cms: '',
    e_ai_solution_type: [],
    e_data_sources: [],
    e_data_volume: '',
    e_local_ai_requirement: '',
    e_gdpr_sensitivity: '',
    e_existing_automation: '',
    e_ai_language: [],
    f_system_type: [],
    f_current_system: '',
    f_dissatisfaction_reasons: [],
    f_custom_vs_ready: '',
    f_concurrent_users: '',
    f_data_migration: '',
    g_systems_to_connect: [],
    g_systems_details: '',
    g_integration_direction: '',
    g_sync_frequency: '',
    g_has_api_docs: '',
    h_security_service_type: [],
    h_had_incident: '',
    h_regulatory_requirements: [],
    i_data_needs: [],
    i_data_sources: [],
    i_existing_bi_tool: '',
    i_report_users: [],
    j_support_type: [],
    j_required_sla: '',
    j_training_type: [],
    j_training_count: '',
    j_training_format: '',
    k_budget_range: '',
    k_pricing_model: '',
    k_launch_deadline: '',
    k_specific_deadline: '',
    k_prefers_mvp: '',
    k_priority: '',
    k_decision_maker: '',
    k_decision_horizon: '',
    l_has_it_team: '',
    l_preferred_stack: [],
    l_hosting_preference: '',
    l_database_preference: '',
    l_cicd_devops: '',
    l_code_ownership: '',
    m_lead_source: '',
    m_next_step: '',
    m_next_contact_date: '',
    m_sales_notes: '',
    m_lead_rating: '',
  };

  allSteps: StepDef[] = [
    { id: 'ai', label: 'AI Import' },
    { id: 'a', label: 'A — Klient' },
    { id: 'b', label: 'B — Typ projektu' },
    { id: 'c', label: 'C — Vyvoj na miru', conditional: true },
    { id: 'd', label: 'D — Web & e-shop', conditional: true },
    { id: 'e', label: 'E — AI & automatizace', conditional: true },
    { id: 'f', label: 'F — Podnikovy system', conditional: true },
    { id: 'g', label: 'G — Integrace', conditional: true },
    { id: 'h', label: 'H — Bezpecnost', conditional: true },
    { id: 'i', label: 'I — Data & analytika', conditional: true },
    { id: 'j', label: 'J — Podpora & skoleni', conditional: true },
    { id: 'k', label: 'K — Rozpocet & cas' },
    { id: 'l', label: 'L — Technicke preference', conditional: true },
    { id: 'm', label: 'M — Zaver hovoru' },
    { id: 'summary', label: 'Shrnuti' },
  ];

  visibleSteps = computed(() => {
    const cats = this.form.b_main_categories;
    const budget = this.form.k_budget_range;
    return this.allSteps.filter((s) => {
      if (!s.conditional) return true;
      switch (s.id) {
        case 'c':
          return cats.includes('custom_dev') || cats.includes('mobile_app');
        case 'd':
          return cats.includes('website_eshop');
        case 'e':
          return cats.includes('ai_automation');
        case 'f':
          return cats.includes('enterprise_system');
        case 'g':
          return cats.includes('integration');
        case 'h':
          return cats.includes('security');
        case 'i':
          return cats.includes('data_analytics');
        case 'j':
          return cats.includes('support') || cats.includes('training');
        case 'l':
          return ['500k_1m', '1m_3m', 'over_3m'].includes(budget);
        default:
          return true;
      }
    });
  });

  activeStepId = computed(() => this.visibleSteps()[this.currentStep()]?.id ?? 'ai');
  totalSteps = computed(() => this.visibleSteps().length);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService,
  ) {}

  ngOnInit(): void {
    this.dealId = Number(this.route.snapshot.paramMap.get('id'));
    this.api.get<DealInfo>(`pipeline/deals/${this.dealId}/`).subscribe({
      next: (deal) => {
        this.dealInfo.set(deal.client_company);
        this.form.a_company_name = deal.client_company || '';
        this.form.a_contact_person = deal.client_contact_name || '';
        this.form.a_email = deal.client_email || '';
        this.form.a_phone = deal.client_phone || '';
        this.form.a_ico = deal.client_ico || '';
      },
    });
  }

  next(): void {
    if (this.currentStep() < this.totalSteps() - 1) {
      this.currentStep.update((s) => s + 1);
      window.scrollTo(0, 0);
    }
  }

  prev(): void {
    if (this.currentStep() > 0) {
      this.currentStep.update((s) => s - 1);
      window.scrollTo(0, 0);
    }
  }

  goToStep(idx: number): void {
    if (idx <= this.currentStep()) {
      this.currentStep.set(idx);
      window.scrollTo(0, 0);
    }
  }

  toggleMulti(arr: string[], value: string): void {
    const idx = arr.indexOf(value);
    if (idx >= 0) arr.splice(idx, 1);
    else arr.push(value);
  }

  isChecked(arr: string[], value: string): boolean {
    return arr.includes(value);
  }

  isAiField(field: string): boolean {
    return this.aiHighlighted().has(field);
  }

  aiExtract(): void {
    const text = this.aiText();
    if (!text.trim()) return;
    this.aiLoading.set(true);
    this.api
      .post<{
        extracted: Record<string, unknown>;
      }>('questionnaire/questionnaires/ai-extract/', { text })
      .subscribe({
        next: (res) => {
          const highlighted = new Set<string>();
          for (const [key, val] of Object.entries(res.extracted)) {
            if (key in this.form && val !== null && val !== undefined) {
              (this.form as Record<string, unknown>)[key] = val;
              highlighted.add(key);
            }
          }
          this.aiHighlighted.set(highlighted);
          this.aiLoading.set(false);
        },
        error: () => this.aiLoading.set(false),
      });
  }

  submit(): void {
    this.submitting.set(true);
    const data = { ...this.form, deal: this.dealId };
    this.api.post('questionnaire/questionnaires/', data).subscribe({
      next: () => this.router.navigate(['/deals', this.dealId]),
      error: () => this.submitting.set(false),
    });
  }
}
