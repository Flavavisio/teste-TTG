/* Total Gest — seleção e apresentação do domínio Armazém/Compras */
(function () {
  'use strict';

  function inventoryViewElements(doc) {
    return {
      articlesTable: doc.getElementById('tabelaArtigos'),
      brandFilter: doc.getElementById('artFiltroMarca'),
      categoryFilter: doc.getElementById('artFiltroCategoria'),
      referenceFilter: doc.getElementById('artFiltroReferencia'),
      textFilter: doc.getElementById('artFiltroTexto'),
      articleCount: doc.getElementById('countArtigos'),
      lowStockCount: doc.getElementById('countStockBaixo'),
      suppliersTable: doc.getElementById('tabelaFornecedores'),
      supplierCount: doc.getElementById('countFornecedores')
    };
  }

  function selectArticlesForTenant(articles, adminId) {
    return (Array.isArray(articles) ? articles : []).filter(function (article) { return article.adminId === adminId; });
  }

  function uniqueSortedValues(list, field) {
    return Array.from(new Set((Array.isArray(list) ? list : []).map(function (item) {
      return (item[field] || '').trim();
    }).filter(Boolean))).sort(function (a, b) { return a.localeCompare(b, 'pt'); });
  }

  function populateFilterSelect(select, values, placeholder, escapeHtml) {
    if (!select) return;
    const current = select.value;
    select.innerHTML = `<option value="">${placeholder}</option>` + values.map(function (value) {
      return `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`;
    }).join('');
    if (values.includes(current)) select.value = current;
  }

  function updateArticleFilterOptions(elements, articles, escapeHtml) {
    if (!elements.brandFilter || !elements.categoryFilter || !elements.referenceFilter) return;
    populateFilterSelect(elements.brandFilter, uniqueSortedValues(articles, 'marca'), 'Todas as marcas', escapeHtml);
    populateFilterSelect(elements.categoryFilter, uniqueSortedValues(articles, 'categoria'), 'Todas as categorias', escapeHtml);
    populateFilterSelect(elements.referenceFilter, uniqueSortedValues(articles, 'referencia'), 'Todas as referências', escapeHtml);
  }

  function articleFilters(elements) {
    return {
      text: ((elements.textFilter && elements.textFilter.value) || '').trim().toLowerCase(),
      brand: (elements.brandFilter && elements.brandFilter.value) || '',
      category: (elements.categoryFilter && elements.categoryFilter.value) || '',
      reference: (elements.referenceFilter && elements.referenceFilter.value) || ''
    };
  }

  function filterArticles(articles, filters) {
    const f=filters || {};
    let list=Array.isArray(articles) ? articles.slice() : [];
    if (f.text) {
      list=list.filter(function (article) {
        return (article.nome || '').toLowerCase().includes(f.text) ||
          (article.marca || '').toLowerCase().includes(f.text) ||
          (article.categoria || '').toLowerCase().includes(f.text) ||
          (article.referencia || '').toLowerCase().includes(f.text);
      });
    }
    if (f.brand) list=list.filter(function (article) { return (article.marca || '').trim() === f.brand; });
    if (f.category) list=list.filter(function (article) { return (article.categoria || '').trim() === f.category; });
    if (f.reference) list=list.filter(function (article) { return (article.referencia || '').trim() === f.reference; });
    return list;
  }

  function articleStockState(article, stock) {
    const minimum=article.stockMinimo;
    const low=minimum != null && stock <= minimum;
    const monitored=article.alertaStock === true;
    const badge=low
      ? `<span style="color:#dc2626;font-weight:700;"><i class="fas fa-exclamation-triangle"></i> Repor${monitored ? ' <i class="fas fa-bell" title="Alerta ativo"></i>' : ''}</span>`
      : `<span style="color:#16a34a;font-weight:600;">OK${monitored ? ' <i class="fas fa-bell" title="Alerta ativo" style="color:#94a3b8;"></i>' : ''}</span>`;
    return { stock: stock, minimum: minimum, low: low, monitored: monitored, badge: badge };
  }

  function articleRowHtml(article, options) {
    const o=options || {};
    const state=articleStockState(article, o.getCurrentStock(article.id));
    const unit=o.getUnitLabel(article.unidade);
    return {
      lowStockAlert: state.low && state.monitored,
      html: `<tr>
                    <td>${o.escapeHtml(article.nome)}</td><td>${o.escapeHtml(article.marca || '—')}</td><td>${o.escapeHtml(article.categoria || '—')}</td><td>${o.escapeHtml(article.referencia || '—')}</td><td>${unit}</td>
                    <td style="font-weight:700;">${state.stock} ${unit}</td><td>${state.minimum != null ? state.minimum : '—'}</td><td>${state.badge}</td>
                    <td><button class="btn btn-sm btn-outline" onclick="abrirModal('artigo','${article.id}')" title="Editar"><i class="fas fa-pen"></i></button>
                        <button class="btn btn-sm btn-outline" onclick="abrirAjusteStock('${article.id}')" title="Ajustar stock"><i class="fas fa-sliders-h"></i></button>
                        <button class="btn btn-sm btn-danger" onclick="eliminarRegisto('artigos','${article.id}')"><i class="fas fa-trash"></i></button></td>
                </tr>`
    };
  }

  function hasArticleFilters(filters) {
    const f=filters || {};
    return !!(f.text || f.brand || f.category || f.reference);
  }

  function renderArticlesArea(options) {
    const o=options || {};
    const elements=inventoryViewElements(o.document);
    if (!elements.articlesTable) return false;
    const tenantArticles=selectArticlesForTenant(o.articles, o.adminId);
    updateArticleFilterOptions(elements, tenantArticles, o.escapeHtml);
    const filters=articleFilters(elements);
    const list=filterArticles(tenantArticles, filters);
    let lowStock=0;
    elements.articlesTable.innerHTML=list.length ? list.map(function (article) {
      const row=articleRowHtml(article, o);
      if (row.lowStockAlert) lowStock++;
      return row.html;
    }).join('') : `<tr><td colspan="9" style="text-align:center;color:#94a3b8;">${hasArticleFilters(filters) ? 'Nenhum artigo corresponde ao filtro.' : 'Sem artigos.'}</td></tr>`;
    if (elements.articleCount) elements.articleCount.textContent=list.length;
    if (elements.lowStockCount) elements.lowStockCount.textContent=lowStock;
    return { list: list, lowStock: lowStock, filters: filters };
  }

  function selectSuppliersForTenant(suppliers, adminId) {
    return (Array.isArray(suppliers) ? suppliers : []).filter(function (supplier) { return supplier.adminId === adminId; });
  }

  function supplierRowHtml(supplier, escapeHtml) {
    return `<tr>
                <td>${escapeHtml(supplier.nome)}</td><td>${escapeHtml(supplier.nif || '—')}</td><td>${escapeHtml(supplier.contacto || '—')}</td><td>${escapeHtml(supplier.email || '—')}</td>
                <td><button class="btn btn-sm btn-outline" onclick="abrirModal('fornecedor','${supplier.id}')"><i class="fas fa-pen"></i></button>
                    <button class="btn btn-sm btn-danger" onclick="eliminarRegisto('fornecedores','${supplier.id}')"><i class="fas fa-trash"></i></button></td>
            </tr>`;
  }

  function renderSuppliersArea(options) {
    const o=options || {};
    const elements=inventoryViewElements(o.document);
    if (!elements.suppliersTable) return false;
    const list=selectSuppliersForTenant(o.suppliers, o.adminId);
    elements.suppliersTable.innerHTML=list.length ? list.map(function (supplier) {
      return supplierRowHtml(supplier, o.escapeHtml);
    }).join('') : '<tr><td colspan="5" style="text-align:center;color:#94a3b8;">Sem fornecedores.</td></tr>';
    if (elements.supplierCount) elements.supplierCount.textContent=list.length;
    return list;
  }

  window.TotalGestInventoryView = {
    inventoryViewElements: inventoryViewElements,
    selectArticlesForTenant: selectArticlesForTenant,
    uniqueSortedValues: uniqueSortedValues,
    populateFilterSelect: populateFilterSelect,
    updateArticleFilterOptions: updateArticleFilterOptions,
    articleFilters: articleFilters,
    filterArticles: filterArticles,
    articleStockState: articleStockState,
    articleRowHtml: articleRowHtml,
    hasArticleFilters: hasArticleFilters,
    renderArticlesArea: renderArticlesArea,
    selectSuppliersForTenant: selectSuppliersForTenant,
    supplierRowHtml: supplierRowHtml,
    renderSuppliersArea: renderSuppliersArea
  };
})();
