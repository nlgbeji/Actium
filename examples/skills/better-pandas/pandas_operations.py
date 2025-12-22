"""高质量 pandas 操作工具函数"""

from typing import Optional, Union, List, Dict, Any, Callable
import pandas as pd
import numpy as np
from pathlib import Path
from actium.skills import skill


@skill(
    category="io",
    examples=[
        "df = load_dataframe('data.csv')",
        "df = load_dataframe('data.xlsx', sheet_name='Sheet1')",
        "df = load_dataframe('data.json', file_type='json')"
    ]
)
def load_dataframe(
    file_path: Union[str, Path],
    file_type: Optional[str] = None,
    **kwargs: Any
) -> pd.DataFrame:
    """
    智能加载数据文件为 DataFrame
    
    根据文件扩展名自动识别文件类型并加载，支持 CSV、Excel、JSON、Parquet 等格式。
    
    Args:
        file_path: 文件路径
        file_type: 文件类型（'csv', 'excel', 'json', 'parquet'），如果为 None 则根据扩展名自动识别
        **kwargs: 传递给相应 pandas 读取函数的额外参数
    
    Returns:
        加载的 DataFrame
    
    Example:
        >>> df = load_dataframe('data.csv')
        >>> df = load_dataframe('data.xlsx', sheet_name='Sheet1')
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 自动识别文件类型
    if file_type is None:
        suffix = file_path.suffix.lower()
        if suffix == '.csv':
            file_type = 'csv'
        elif suffix in ['.xlsx', '.xls']:
            file_type = 'excel'
        elif suffix == '.json':
            file_type = 'json'
        elif suffix == '.parquet':
            file_type = 'parquet'
        elif suffix == '.feather':
            file_type = 'feather'
        else:
            raise ValueError(f"不支持的文件类型: {suffix}")
    
    # 根据类型加载
    if file_type == 'csv':
        return pd.read_csv(file_path, **kwargs)
    elif file_type == 'excel':
        return pd.read_excel(file_path, **kwargs)
    elif file_type == 'json':
        return pd.read_json(file_path, **kwargs)
    elif file_type == 'parquet':
        return pd.read_parquet(file_path, **kwargs)
    elif file_type == 'feather':
        return pd.read_feather(file_path, **kwargs)
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")


@skill(
    category="io",
    examples=[
        "save_dataframe(df, 'output.csv')",
        "save_dataframe(df, 'output.xlsx', index=False)",
        "save_dataframe(df, 'output.json', file_type='json', orient='records')"
    ]
)
def save_dataframe(
    df: pd.DataFrame,
    file_path: Union[str, Path],
    file_type: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    智能保存 DataFrame 到文件
    
    根据文件扩展名自动识别文件类型并保存，支持 CSV、Excel、JSON、Parquet 等格式。
    
    Args:
        df: 要保存的 DataFrame
        file_path: 保存路径
        file_type: 文件类型（'csv', 'excel', 'json', 'parquet'），如果为 None 则根据扩展名自动识别
        **kwargs: 传递给相应 pandas 保存函数的额外参数
    
    Returns:
        None
    
    Example:
        >>> save_dataframe(df, 'output.csv')
        >>> save_dataframe(df, 'output.xlsx', index=False)
    """
    file_path = Path(file_path)
    
    # 自动识别文件类型
    if file_type is None:
        suffix = file_path.suffix.lower()
        if suffix == '.csv':
            file_type = 'csv'
        elif suffix in ['.xlsx', '.xls']:
            file_type = 'excel'
        elif suffix == '.json':
            file_type = 'json'
        elif suffix == '.parquet':
            file_type = 'parquet'
        elif suffix == '.feather':
            file_type = 'feather'
        else:
            raise ValueError(f"不支持的文件类型: {suffix}")
    
    # 确保目录存在
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 根据类型保存
    if file_type == 'csv':
        df.to_csv(file_path, **kwargs)
    elif file_type == 'excel':
        df.to_excel(file_path, **kwargs)
    elif file_type == 'json':
        df.to_json(file_path, **kwargs)
    elif file_type == 'parquet':
        df.to_parquet(file_path, **kwargs)
    elif file_type == 'feather':
        df.to_feather(file_path, **kwargs)
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")


@skill(
    category="exploration",
    examples=[
        "summary = explore_dataframe(df)",
        "summary = explore_dataframe(df, include_stats=True)"
    ]
)
def explore_dataframe(
    df: pd.DataFrame,
    include_stats: bool = True,
    sample_size: int = 5
) -> Dict[str, Any]:
    """
    快速探索 DataFrame 的基本信息
    
    返回包含形状、列信息、缺失值、数据类型等信息的字典。
    
    Args:
        df: 要探索的 DataFrame
        include_stats: 是否包含数值列的统计信息
        sample_size: 显示的前 N 行样本数量
    
    Returns:
        包含探索信息的字典
    
    Example:
        >>> info = explore_dataframe(df)
        >>> print(f"形状: {info['shape']}, 列数: {info['n_columns']}")
    """
    info: Dict[str, Any] = {
        'shape': df.shape,
        'n_rows': len(df),
        'n_columns': len(df.columns),
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'missing_values': df.isnull().sum().to_dict(),
        'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
        'sample': df.head(sample_size).to_dict('records'),
    }
    
    if include_stats:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            info['numeric_stats'] = df[numeric_cols].describe().to_dict()
    
    return info


@skill(
    category="cleaning",
    examples=[
        "df_clean = clean_dataframe(df)",
        "df_clean = clean_dataframe(df, drop_duplicates=True, fill_method='mean')"
    ]
)
def clean_dataframe(
    df: pd.DataFrame,
    drop_duplicates: bool = True,
    fill_method: Optional[str] = None,
    remove_outliers: bool = False,
    outlier_method: str = 'iqr'
) -> pd.DataFrame:
    """
    清理 DataFrame 数据
    
    执行常见的数据清理操作：去重、填充缺失值、移除异常值等。
    
    Args:
        df: 要清理的 DataFrame
        drop_duplicates: 是否删除重复行
        fill_method: 填充缺失值的方法（'mean', 'median', 'mode', 'forward', 'backward'），None 表示不填充
        remove_outliers: 是否移除异常值
        outlier_method: 异常值检测方法（'iqr' 或 'zscore'）
    
    Returns:
        清理后的 DataFrame
    
    Example:
        >>> df_clean = clean_dataframe(df, drop_duplicates=True, fill_method='mean')
    """
    df_clean = df.copy()
    
    # 去重
    if drop_duplicates:
        df_clean = df_clean.drop_duplicates()
    
    # 填充缺失值
    if fill_method:
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        if fill_method == 'mean':
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
        elif fill_method == 'median':
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
        elif fill_method == 'mode':
            for col in numeric_cols:
                mode_val = df_clean[col].mode()
                if len(mode_val) > 0:
                    df_clean[col] = df_clean[col].fillna(mode_val[0])
        elif fill_method == 'forward':
            df_clean = df_clean.fillna(method='ffill')
        elif fill_method == 'backward':
            df_clean = df_clean.fillna(method='bfill')
    
    # 移除异常值
    if remove_outliers:
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if outlier_method == 'iqr':
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
            elif outlier_method == 'zscore':
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                df_clean = df_clean[z_scores < 3]
    
    return df_clean


@skill(
    category="transformation",
    examples=[
        "df_normalized = normalize_columns(df, columns=['age', 'income'])",
        "df_normalized = normalize_columns(df, method='minmax')"
    ]
)
def normalize_columns(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = 'standard'
) -> pd.DataFrame:
    """
    标准化数值列
    
    对指定的数值列进行标准化处理，支持 Z-score 标准化和 Min-Max 标准化。
    
    Args:
        df: 要处理的 DataFrame
        columns: 要标准化的列名列表，如果为 None 则标准化所有数值列
        method: 标准化方法（'standard' 为 Z-score，'minmax' 为 Min-Max）
    
    Returns:
        标准化后的 DataFrame
    
    Example:
        >>> df_norm = normalize_columns(df, columns=['age', 'income'], method='standard')
    """
    df_result = df.copy()
    
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in columns:
        if col not in df.columns:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        
        if method == 'standard':
            # Z-score 标准化
            mean = df_result[col].mean()
            std = df_result[col].std()
            if std != 0:
                df_result[col] = (df_result[col] - mean) / std
        elif method == 'minmax':
            # Min-Max 标准化
            min_val = df_result[col].min()
            max_val = df_result[col].max()
            if max_val != min_val:
                df_result[col] = (df_result[col] - min_val) / (max_val - min_val)
    
    return df_result


@skill(
    category="aggregation",
    examples=[
        "summary = aggregate_by_group(df, group_by='category', agg_funcs={'price': 'mean', 'quantity': 'sum'})",
        "summary = aggregate_by_group(df, group_by=['category', 'region'])"
    ]
)
def aggregate_by_group(
    df: pd.DataFrame,
    group_by: Union[str, List[str]],
    agg_funcs: Optional[Dict[str, Union[str, List[str]]]] = None,
    sort: bool = True
) -> pd.DataFrame:
    """
    按组聚合数据
    
    对 DataFrame 按指定列分组并执行聚合操作。
    
    Args:
        df: 要聚合的 DataFrame
        group_by: 分组列名或列名列表
        agg_funcs: 聚合函数字典，格式为 {列名: 聚合函数}，如果为 None 则对所有数值列求均值
        sort: 是否对结果排序
    
    Returns:
        聚合后的 DataFrame
    
    Example:
        >>> summary = aggregate_by_group(df, group_by='category', agg_funcs={'price': 'mean', 'quantity': 'sum'})
    """
    if agg_funcs is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        agg_funcs = {col: 'mean' for col in numeric_cols}
    
    result = df.groupby(group_by).agg(agg_funcs).reset_index()
    
    if sort:
        if isinstance(group_by, str):
            result = result.sort_values(group_by)
        else:
            result = result.sort_values(group_by[0])
    
    return result


@skill(
    category="merging",
    examples=[
        "df_merged = merge_dataframes(df1, df2, on='id')",
        "df_merged = merge_dataframes(df1, df2, left_on='id1', right_on='id2', how='outer')"
    ]
)
def merge_dataframes(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: Optional[Union[str, List[str]]] = None,
    left_on: Optional[Union[str, List[str]]] = None,
    right_on: Optional[Union[str, List[str]]] = None,
    how: str = 'inner',
    suffixes: tuple = ('_x', '_y')
) -> pd.DataFrame:
    """
    合并两个 DataFrame
    
    提供更友好的接口来合并两个 DataFrame，支持多种合并方式。
    
    Args:
        left: 左侧 DataFrame
        right: 右侧 DataFrame
        on: 用于合并的列名（两个 DataFrame 都有该列时使用）
        left_on: 左侧 DataFrame 用于合并的列名
        right_on: 右侧 DataFrame 用于合并的列名
        how: 合并方式（'left', 'right', 'outer', 'inner'）
        suffixes: 重复列名的后缀
    
    Returns:
        合并后的 DataFrame
    
    Example:
        >>> df_merged = merge_dataframes(df1, df2, on='id', how='outer')
    """
    return pd.merge(
        left, right,
        on=on,
        left_on=left_on,
        right_on=right_on,
        how=how,
        suffixes=suffixes
    )


@skill(
    category="filtering",
    examples=[
        "df_filtered = filter_dataframe(df, conditions={'age': ('>=', 18), 'city': ('==', 'Beijing')})",
        "df_filtered = filter_dataframe(df, query='age >= 18 and city == \"Beijing\"')"
    ]
)
def filter_dataframe(
    df: pd.DataFrame,
    conditions: Optional[Dict[str, tuple]] = None,
    query: Optional[str] = None
) -> pd.DataFrame:
    """
    根据条件过滤 DataFrame
    
    支持字典条件或 pandas query 字符串两种方式过滤数据。
    
    Args:
        df: 要过滤的 DataFrame
        conditions: 条件字典，格式为 {列名: (操作符, 值)}，操作符支持 '==', '!=', '>', '<', '>=', '<=', 'in', 'not in'
        query: pandas query 字符串（如果提供，将优先使用此方式）
    
    Returns:
        过滤后的 DataFrame
    
    Example:
        >>> df_filtered = filter_dataframe(df, conditions={'age': ('>=', 18), 'status': ('==', 'active')})
        >>> df_filtered = filter_dataframe(df, query='age >= 18 and status == "active"')
    """
    if query:
        return df.query(query)
    
    if conditions is None:
        return df
    
    result = df.copy()
    for col, (op, value) in conditions.items():
        if col not in df.columns:
            continue
        
        if op == '==':
            result = result[result[col] == value]
        elif op == '!=':
            result = result[result[col] != value]
        elif op == '>':
            result = result[result[col] > value]
        elif op == '<':
            result = result[result[col] < value]
        elif op == '>=':
            result = result[result[col] >= value]
        elif op == '<=':
            result = result[result[col] <= value]
        elif op == 'in':
            result = result[result[col].isin(value)]
        elif op == 'not in':
            result = result[~result[col].isin(value)]
    
    return result


@skill(
    category="transformation",
    examples=[
        "df_pivot = pivot_dataframe(df, index='date', columns='category', values='sales')",
        "df_pivot = pivot_dataframe(df, index=['date', 'region'], values='sales')"
    ]
)
def pivot_dataframe(
    df: pd.DataFrame,
    index: Union[str, List[str]],
    columns: Optional[Union[str, List[str]]] = None,
    values: Optional[Union[str, List[str]]] = None,
    aggfunc: Union[str, Callable, List[Union[str, Callable]]] = 'mean',
    fill_value: Optional[Any] = None
) -> pd.DataFrame:
    """
    透视表转换
    
    将 DataFrame 转换为透视表格式，便于数据分析和可视化。
    
    Args:
        df: 要转换的 DataFrame
        index: 作为行索引的列名或列名列表
        columns: 作为列索引的列名或列名列表
        values: 要聚合的列名或列名列表
        aggfunc: 聚合函数（'mean', 'sum', 'count' 等）
        fill_value: 用于填充缺失值的值
    
    Returns:
        透视表 DataFrame
    
    Example:
        >>> df_pivot = pivot_dataframe(df, index='date', columns='category', values='sales', aggfunc='sum')
    """
    return df.pivot_table(
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc,
        fill_value=fill_value
    )

